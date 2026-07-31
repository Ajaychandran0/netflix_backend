import asyncio
from pathlib import Path

from app.core.config import dynamic_config
from app.core.logger import configure_logging, logger

from app.constants.processing import ProcessingStage
from app.constants.assets import TRANSCODER_OUTPUT_DIR
from app.constants.transcoding import TRANSCODING_RESOLUTIONS

from app.schemas.events import (
    ProcessingStartedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent,
)
from app.schemas.video import VideoMetadata
from app.schemas.assets import UploadedAssets

from app.messaging.video_event_publisher import VideoEventPublisher
from app.tracking.status_tracker import StatusTracker

from app.processor.pipeline.progress_coordinator import TranscodingProgressCoordinator
from app.processor.pipeline.stage_manager import StageManager

from app.processor.downloader import download_source_video
from app.processor.metadata_extractor import extract_video_metadata
from app.processor.video_transcoder import transcode_video_to_hls
from app.processor.master_playlist_generator import generate_master_playlist
from app.processor.thumbnail_generator import generate_thumbnail
from app.processor.uploader import upload_transcoded_outputs
from app.processor.cleaner import cleanup


configure_logging()


async def main():
    publisher = None
    tracker = None
    stage_manager = None
    progress_coordinator = None
    video_id = None
    
    current_stage = ProcessingStage.DOWNLOADING

    try:
        # ------------------------------------------------------------------
        # Read environment variables
        # ------------------------------------------------------------------
        video_id = dynamic_config.video_id
        upload_path = dynamic_config.upload_path

        logger.info(
            "Starting transcoding for video %s",
            video_id,
        )

        # --------------------------------------------------
        # Initialize infrastructure
        # --------------------------------------------------
        publisher = VideoEventPublisher()

        tracker = StatusTracker(video_id)

        stage_manager = StageManager(
            video_id=video_id,
            tracker=tracker,
            publisher=publisher,
        )
        
        progress_coordinator = (
            TranscodingProgressCoordinator(
                resolutions=TRANSCODING_RESOLUTIONS,
                status_tracker=tracker,
            )
        )

        # ------------------------------------------------------------------
        # Processing started
        # ------------------------------------------------------------------
        await tracker.start()

        publisher.publish_processing_started(
            ProcessingStartedEvent(
                video_id=video_id,
            )
        )

        # ------------------------------------------------------------------
        # Download
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.DOWNLOADING
        await stage_manager.transition_to(current_stage)

        local_input_path: Path = download_source_video(upload_path) 
        
        # ------------------------------------------------------------------
        # Extract metadata
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.EXTRACTING_METADATA
        await stage_manager.transition_to(current_stage)

        video_metadata: VideoMetadata = extract_video_metadata(local_input_path)

        # ------------------------------------------------------------------
        # Transcoding
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.TRANSCODING
        await stage_manager.transition_to(current_stage)
  
        output_map: dict[str, Path] = await transcode_video_to_hls(
            input_path=local_input_path,
            output_base_dir=TRANSCODER_OUTPUT_DIR,
            resolutions=TRANSCODING_RESOLUTIONS,
            video_metadata=video_metadata,
            progress_callback=progress_coordinator.on_progress,
        )
        
        
        # ------------------------------------------------------------------
        # Master playlist
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.GENERATING_PLAYLIST
        await stage_manager.transition_to(current_stage)

        local_master_playlist_path: Path = generate_master_playlist(
            output_map=output_map,
            output_dir=TRANSCODER_OUTPUT_DIR,
        )

        # ------------------------------------------------------------------
        # Thumbnail
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.GENERATING_THUMBNAIL
        await stage_manager.transition_to(current_stage)

        local_thumbnail_path: Path = generate_thumbnail(
            local_input_path,
            duration_ms=video_metadata.duration_ms,
        )

        # ------------------------------------------------------------------
        # Upload assets
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.UPLOADING_ASSETS
        await stage_manager.transition_to(current_stage)

        uploaded_assets: UploadedAssets = upload_transcoded_outputs(
            video_id=video_id,
            output_dir=TRANSCODER_OUTPUT_DIR,
            local_master_playlist_path=local_master_playlist_path,
            local_thumbnail_path=local_thumbnail_path,
        )

        # ------------------------------------------------------------------
        # Cleanup
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.CLEANUP
        await stage_manager.transition_to(current_stage)

        cleanup(upload_path=upload_path)

        publisher.publish_processing_completed(
            ProcessingCompletedEvent(
                video_id=video_id,
                master_playlist_object_key=uploaded_assets.master_playlist_object_key,
                thumbnail_object_key=uploaded_assets.thumbnail_object_key,
                duration_ms=video_metadata.duration_ms,
                source_width=video_metadata.source_width,
                source_height=video_metadata.source_height,
                source_file_size_bytes=video_metadata.source_file_size_bytes,
                mime_type=video_metadata.mime_type,
            )
        )
        
        await tracker.complete()

        logger.info(
            "Transcoding completed successfully for video %s",
            video_id,
        )

    except Exception as e:
        logger.exception(
            "Fatal error during transcoding: %s",
            e,
        )

        if tracker:
            await tracker.fail(current_stage)

        if publisher and video_id:
            publisher.publish_processing_failed(
                ProcessingFailedEvent(
                    video_id=video_id,
                    current_stage=current_stage,
                    error=str(e),
                )
            )

        raise


if __name__ == "__main__":
    asyncio.run(main())