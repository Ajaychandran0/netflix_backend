import sys
import asyncio
from app.core.config import static_config, dynamic_config
from app.core.logger import configure_logging, logger
from app.transcoder.downloader import download_video_from_s3
from app.transcoder.transcoder import transcode_video_to_hls
from app.transcoder.master_playlist import generate_master_playlist
from app.transcoder.thumbnail import generate_thumbnail
from app.transcoder.uploader import upload_transcoded_outputs
from app.transcoder.status_tracker import StatusTracker
from app.services.video.video_event_publisher import VideoEventPublisher
from app.constants.processing_stage import ProcessingStage
from app.schemas.video_events import (
    ProcessingStartedEvent,
    StageChangedEvent,
    ProcessingCompletedEvent,
    ProcessingFailedEvent
)

configure_logging()

async def main():
    try:
        # 1. Read environment variables
        video_id = dynamic_config.video_id
        user_id = dynamic_config.user_id
        upload_path = dynamic_config.upload_path
        title = dynamic_config.title
        thumbnail_object_key = dynamic_config.thumbnail_object_key
        publisher = VideoEventPublisher()

        # event = Event(video_id, user_id, upload_path, title, thumbnail_object_key)
        print(f"Received event for video_id: {video_id}, user_id: {user_id}, upload_path: {upload_path}")
        logger.info(f"Starting transcoding for video: {video_id}")
        started_event = ProcessingStartedEvent(video_id=video_id)
        publisher.publish_processing_started(started_event)

        # 2. Init Redis status tracker
        # tracker = StatusTracker(video_id, redis_client)
        # await tracker.set_stage("downloading")

        # 3. Download video from MinIO/S3
        current_stage = ProcessingStage.DOWNLOADING
        stage_changed_event = StageChangedEvent(video_id=video_id, stage=current_stage)
        publisher.publish_stage_changed(stage_changed_event)
        local_input_path = download_video_from_s3(upload_path)

        # 4. Transcode to multiple resolutions
        current_stage = ProcessingStage.TRANSCODING
        stage_changed_event = StageChangedEvent(video_id=video_id, stage=current_stage)
        publisher.publish_stage_changed(stage_changed_event)
        
        # await tracker.set_stage("transcoding")
        output_map = await transcode_video_to_hls(
            input_path=local_input_path,
            output_base_dir=static_config.s3_transcoded_base_path,
            # tracker=tracker,
            resolutions=["240p", "360p", "480p", "720p", "1080p"]
            # delay_hd=True,
        )
          
        # create_master_playlist
        current_stage = ProcessingStage.GENERATING_PLAYLIST
        stage_changed_event = StageChangedEvent(video_id=video_id, stage=current_stage)
        publisher.publish_stage_changed(stage_changed_event)
        
        master_path = generate_master_playlist(
            output_map=output_map,
            output_dir=static_config.s3_transcoded_base_path
        )

        # 5. Generate thumbnail (if needed)
        # await tracker.set_stage("thumbnail")
        current_stage = ProcessingStage.GENERATING_THUMBNAIL
        stage_changed_event = StageChangedEvent(video_id=video_id, stage=current_stage)
        publisher.publish_stage_changed(stage_changed_event)
        
        generate_thumbnail(
            local_input_path, f"{static_config.s3_transcoded_base_path}/thumbnail.jpg"
        )

        # 6. Upload everything to final destination
        # await tracker.set_stage("uploading")
        current_stage = ProcessingStage.UPLOADING_ASSETS
        stage_changed_event = StageChangedEvent(video_id=video_id, stage=current_stage)
        publisher.publish_stage_changed(stage_changed_event)

        upload_transcoded_outputs(
            video_id=video_id,
            local_output_dir=static_config.s3_transcoded_base_path,
        )
        
        # 7. Clean up
        current_stage = ProcessingStage.CLEANUP
        stage_changed_event = StageChangedEvent(video_id=video_id, stage=current_stage)
        publisher.publish_stage_changed(stage_changed_event)

        # await tracker.set_stage("cleanup")
        # await cleanup_temp_files([local_input_path, thumbnail_path, *transcoded_outputs.values()])
        # await tracker.set_stage("completed")

        completed_event = ProcessingCompletedEvent(
            video_id=video_id,
            master_playlist_key=master_path,
            thumbnail_object_key=thumbnail_object_key,
            duration_ms=0,  # Replace with actual duration
            source_width=0,  # Replace with actual width
            source_height=0,  # Replace with actual height
        )
        
        publisher.publish_processing_completed(completed_event)

      

        logger.info(f"Transcoding completed successfully for video {video_id}")

    except Exception as e:
        logger.exception(f"Fatal error during transcoding: {e}")
        failed_event = ProcessingFailedEvent(
            video_id=video_id,
            current_stage=current_stage,
            error=str(e)
        )
        publisher.publish_processing_failed(failed_event)
        # if "video_id" in locals():
        #     tracker = StatusTracker(video_id, redis_client)
        #     await tracker.set_stage("failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
