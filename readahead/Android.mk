LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

LOCAL_SRC_FILES := readahead.c
LOCAL_CFLAGS += -g
LOCAL_MODULE := readahead

include $(BUILD_EXECUTABLE)
