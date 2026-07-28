import asyncio

from app.core.config import static_config, dynamic_config
from app.core.logger import configure_logging, logger

from app.constants.processing_stage import ProcessingStage

from app.schemas.video_events import (
    ProcessingStartedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent,
)

from app.services.video.video_event_publisher import VideoEventPublisher
from app.transcoder.status_tracker import StatusTracker
from app.transcoder.stage_manager import StageManager

from app.transcoder.downloader import download_video_from_s3
from app.transcoder.transcoder import transcode_video_to_hls
from app.transcoder.master_playlist import generate_master_playlist
from app.transcoder.thumbnail import generate_thumbnail
from app.transcoder.uploader import upload_transcoded_outputs


configure_logging()


async def main():
    publisher = None
    tracker = None
    stage_manager = None
    video_id = None
    
    current_stage = ProcessingStage.DOWNLOADING

    try:
        # ------------------------------------------------------------------
        # Read environment variables
        # ------------------------------------------------------------------
        video_id = dynamic_config.video_id
        upload_path = dynamic_config.upload_path
        thumbnail_object_key = dynamic_config.thumbnail_object_key
        # user_id = dynamic_config.user_id
        # title = dynamic_config.title

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
        await stage_manager.transition_to(
            current_stage,
            progress=5,
        )

        local_input_path = download_video_from_s3(upload_path) 

        # ------------------------------------------------------------------
        # Transcoding
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.TRANSCODING
        await stage_manager.transition_to(
            current_stage,
            progress=10,
        )

        output_map = await transcode_video_to_hls(
            input_path=local_input_path,
            output_base_dir=static_config.s3_transcoded_base_path,
            resolutions=[
                "240p",
                "360p",
                "480p",
                "720p",
                "1080p",
            ],
        )

        # ------------------------------------------------------------------
        # Master playlist
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.GENERATING_PLAYLIST
        await stage_manager.transition_to(
            current_stage,
            progress=85,
        )

        master_path = generate_master_playlist(
            output_map=output_map,
            output_dir=static_config.s3_transcoded_base_path,
        )

        # ------------------------------------------------------------------
        # Thumbnail
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.GENERATING_THUMBNAIL
        await stage_manager.transition_to(
            current_stage,
            progress=90,
        )

        generate_thumbnail(
            local_input_path,
            f"{static_config.s3_transcoded_base_path}/thumbnail.jpg",
        )

        # ------------------------------------------------------------------
        # Upload assets
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.UPLOADING_ASSETS
        await stage_manager.transition_to(
            current_stage,
            progress=93,
        )

        upload_transcoded_outputs(
            video_id=video_id,
            local_output_dir=static_config.s3_transcoded_base_path,
        )

        # ------------------------------------------------------------------
        # Cleanup
        # ------------------------------------------------------------------
        current_stage = ProcessingStage.CLEANUP

        await stage_manager.transition_to(
            current_stage,
            progress=98,
        )

        publisher.publish_processing_completed(
            ProcessingCompletedEvent(
                video_id=video_id,
                master_playlist_key=master_path,
                thumbnail_object_key=thumbnail_object_key,
                duration_ms=0,
                source_width=0,
                source_height=0,
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