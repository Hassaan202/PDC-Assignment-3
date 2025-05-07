EXECUTABLE := render

CU_FILES   := cudaRenderer.cu benchmark.cu

CU_DEPS    :=

CC_FILES   := main.cpp display.cpp refRenderer.cpp \
              noise.cpp ppm.cpp sceneLoader.cpp

LOGS	   := logs

###########################################################

# Colab environment settings
OBJDIR=objs
CXXFLAGS=-O3 -Wall -g
HOSTNAME=$(shell hostname)

# Libraries - only CUDA, no OpenGL
LIBS       := cudart
FRAMEWORKS :=

# Define NO_OPENGL to use headless mode
CXXFLAGS += -DNO_OPENGL

# CUDA settings for Colab T4
NVCC=nvcc
NVCCFLAGS=-O3 --gpu-architecture=compute_75 --gpu-code=sm_75
CUDA_PATH=/usr/local/cuda

# Colab CUDA paths
LDFLAGS=-L$(CUDA_PATH)/lib64/ -lcudart
CUDA_INCLUDE_PATH=$(CUDA_PATH)/include

# Add CUDA include path
CXXFLAGS += -I$(CUDA_INCLUDE_PATH)

LDLIBS  := $(addprefix -l, $(LIBS))
LDFRAMEWORKS := $(addprefix -framework , $(FRAMEWORKS))

OBJS=$(OBJDIR)/main.o $(OBJDIR)/display.o $(OBJDIR)/benchmark.o $(OBJDIR)/refRenderer.o \
     $(OBJDIR)/cudaRenderer.o $(OBJDIR)/noise.o $(OBJDIR)/ppm.o $(OBJDIR)/sceneLoader.o


.PHONY: dirs clean

default: $(EXECUTABLE)

dirs:
	mkdir -p $(OBJDIR)/

clean:
	rm -rf $(OBJDIR) *~ $(EXECUTABLE) $(LOGS)

$(EXECUTABLE): dirs $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS) $(LDFLAGS) $(LDLIBS) $(LDFRAMEWORKS)

$(OBJDIR)/%.o: %.cpp
	$(CXX) $< $(CXXFLAGS) -c -o $@

$(OBJDIR)/%.o: %.cu
	$(NVCC) $< $(NVCCFLAGS) -c -o $@