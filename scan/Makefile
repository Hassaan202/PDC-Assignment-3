EXECUTABLE := cudaScan

CU_FILES   := scan.cu
CU_DEPS    :=
CC_FILES   := main.cpp

all: $(EXECUTABLE)

LOGS	   := logs

###########################################################

OBJDIR=objs
CXX=g++
CXXFLAGS=-O3 -Wall
LDFLAGS=-L/usr/local/cuda/lib64/ -lcudart
NVCC=/usr/local/cuda/bin/nvcc
# T4 GPU uses Turing architecture (sm_75)
NVCCFLAGS=-O3 --gpu-architecture=compute_75 --gpu-code=sm_75

OBJS=$(OBJDIR)/main.o $(OBJDIR)/scan.o

.PHONY: dirs clean

default: $(EXECUTABLE)

dirs:
	mkdir -p $(OBJDIR)/

clean:
	rm -rf $(OBJDIR) *.ppm *~ $(EXECUTABLE) $(LOGS)

$(EXECUTABLE): dirs $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS) $(LDFLAGS)

$(OBJDIR)/%.o: %.cpp
	$(CXX) $< $(CXXFLAGS) -c -o $@

$(OBJDIR)/%.o: %.cu
	$(NVCC) $< $(NVCCFLAGS) -c -o $@