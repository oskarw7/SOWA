#include <gst/gst.h>
#include <glib.h>
#include <stdio.h>
#include <signal.h>
#include <fstream>
#include "nvdsmeta.h"
#include "gstnvdsmeta.h"

#define FRAME_WIDTH 1920 //3840
#define FRAME_HEIGHT 1080 //2160

// Comment out to hide the FPS counter
#define SHOW_FPS

#ifdef SHOW_FPS
static guint frameCount = 0;
static gint64 startTime = 0;
#endif

// Global pointer to the main loop to allow the signal handler to stop it
static GMainLoop *mainLoop = NULL;

//std::ofstream outputPipeToMm("/tmp/rura");

// Signal handler function for the SIGINT signal
static void handleInterrupt(int sig) {
    g_print("\nInterrupt signal (%d) received.\n", sig);
    if (mainLoop) {
        g_main_loop_quit(mainLoop);
    }
}

// Buffer probe function to extract and process metadata from the OSD sink pad
static GstPadProbeReturn probe(GstPad *pad, GstPadProbeInfo *info, gpointer u_data) {
    GstBuffer *buf = (GstBuffer *)info->data;
    NvDsBatchMeta *batchMeta = gst_buffer_get_nvds_batch_meta(buf);
    
    if (!batchMeta) {
        return GST_PAD_PROBE_OK;
    }

#ifdef SHOW_FPS
    if (startTime == 0) startTime = g_get_monotonic_time();
    
    frameCount++;

    if (frameCount % 30 == 0) {
        gint64 currentTime = g_get_monotonic_time();
        double elapsedSec = (currentTime - startTime) / 1000000.0;
        double fps = 30.0 / elapsedSec;
        
        fprintf(stderr, "\rFPS: %.2f", fps);
        
        startTime = currentTime;
    }
#endif

    // Traverse through frames in the current batch
    for (NvDsMetaList *lFrame = batchMeta->frame_meta_list; lFrame != NULL; lFrame = lFrame->next) {
        NvDsFrameMeta *frameMeta = (NvDsFrameMeta *)(lFrame->data);
        
        // Calculate center of the source frame
        float centerX = frameMeta->source_frame_width / 2.0;
        float centerY = frameMeta->source_frame_height / 2.0;

        // Traverse through detected objects in the frame
        for (NvDsMetaList *lObj = frameMeta->obj_meta_list; lObj != NULL; lObj = lObj->next) {
            NvDsObjectMeta *objMeta = (NvDsObjectMeta *)(lObj->data);
            
             // Calculate offsets from the image center to the object center
            float offsetX = (objMeta->rect_params.left + objMeta->rect_params.width / 2.0) - centerX;
            float offsetY = (-1.0)*((objMeta->rect_params.top + objMeta->rect_params.height / 2.0) - centerY);

            // printf("DATA|ID:%lu|CLS:%d|CONF:%.2f|X:%.1f|Y:%.1f\n", objMeta->object_id, objMeta->class_id, objMeta->confidence, offsetX, offsetY);
            //printf("%d %d\n", static_cast<int>(offsetX), static_cast<int>(offsetY));
            //outputPipeToMm << static_cast<int>(offsetX) << " " << static_cast<int>(offsetY) << "\n";
            //outputPipeToMm.flush();
            // printf("DATA|ID:%lu|CLS:%d|CONF:%.2f|X:%.1f|Y:%.1f\n", objMeta->object_id, objMeta->class_id, objMeta->confidence, offsetX, offsetY);
        }
    }
    return GST_PAD_PROBE_OK;
}

int main(int argc, char *argv[]) {
    // Validate input arguments
    if (argc < 3) {
        g_printerr("Usage: %s <config_nvinfer.txt> <input_uri>\n", argv[0]);
        return -1;
    }

    // Initialize GStreamer framework
    gst_init(&argc, &argv);

    /* Build the visual pipeline using hardware-accelerated elements:
     *  nvurisrcbin: Obtaining frames from a camera or video.
     *  nvstreammux: Batching multiple streams (even if single source).
     *  nvinfer: Primary Inference Engine (YOLO).
     *  nvtracker: DCF-based high-performance object tracking.
     *  nvdsosd: On-Screen Display for drawing bounding boxes and labels.
     *  nv3dsink: High-performance renderer for Jetson.
     */
    gchar *pipelineDesc = g_strdup_printf(
        "nvurisrcbin uri=%s latency=100 ! "
        "queue name=q_dec ! "
        "mux.sink_0 nvstreammux name=mux batch-size=1 width=%d height=%d batched-push-timeout=40000 ! "
        "queue name=q_mux ! "
        "nvinfer name=primary-infer config-file-path=%s ! "
        "queue name=q_infer ! "
        "nvtracker name=tracker tracker-width=640 tracker-height=384 "
        "ll-lib-file=/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so "
        "ll-config-file=/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/config_tracker_NvDCF_perf.yml ! "
        "queue name=q_tracker ! "
        "nvvideoconvert ! nvdsosd name=osd ! nvvideoconvert ! "
        "queue name=q_render ! "
        "nv3dsink sync=false", 
        argv[2], FRAME_WIDTH, FRAME_HEIGHT, argv[1]);

    GError *error = NULL;
    GstElement *pipeline = gst_parse_launch(pipelineDesc, &error);
    
    if (error) {
        g_printerr("Pipeline launch error: %s\n", error->message);
        g_error_free(error);
        return -1;
    }

    // Attach the analytics probe to the OSD sink pad to intercept data before rendering
    GstElement *osdElement = gst_bin_get_by_name(GST_BIN(pipeline), "osd");
    GstPad *osdPad = gst_element_get_static_pad(osdElement, "sink");
    gst_pad_add_probe(osdPad, GST_PAD_PROBE_TYPE_BUFFER, probe, NULL, NULL);

    // Init the main event loop
    mainLoop = g_main_loop_new(NULL, FALSE);

    // Register the handleInterrupt function for the SIGINT signal
    signal(SIGINT, handleInterrupt);

    // Start playback
    gst_element_set_state(pipeline, GST_STATE_PLAYING);
    fprintf(stderr, "Pipeline is running. Visual output enabled.\n");

    // Run the main loop
    g_main_loop_run(mainLoop);

    // Clean up
    gst_element_set_state(pipeline, GST_STATE_NULL);
    gst_object_unref(pipeline);
    g_main_loop_unref(mainLoop);

    return 0;
}