EXECUTABLE := cudaSaxpy

CU_FILES   := saxpy.cu
CU_DEPS    :=
CC_FILES   := main.cpp

###########################################################
OBJDIR=objs
CXX=g++
CXXFLAGS=-O3 -Wall
LDFLAGS=-L/usr/local/cuda/lib64 -lcudart
NVCC=/usr/local/cuda/bin/nvcc
# T4 GPU uses Turing architecture which is sm_75
NVCCFLAGS=-O3 --gpu-architecture=compute_75 --gpu-code=sm_75

OBJS=$(OBJDIR)/main.o $(OBJDIR)/saxpy.o

.PHONY: dirs clean

default: $(EXECUTABLE)

dirs:
	mkdir -p $(OBJDIR)

clean:
	rm -rf $(OBJDIR) *.ppm *~ $(EXECUTABLE)

$(EXECUTABLE): dirs $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS) $(LDFLAGS)

$(OBJDIR)/%.o: %.cpp
	$(CXX) $< $(CXXFLAGS) -c -o $@

$(OBJDIR)/%.o: %.cu
	$(NVCC) $< $(NVCCFLAGS) -c -o $@