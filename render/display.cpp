#include <algorithm>
#include <stdio.h>
#include "circleRenderer.h"
#include "cycleTimer.h"
#include "image.h"

#ifdef NO_OPENGL
// No OpenGL version

void renderPicture();

static struct {
    int width;
    int height;
    bool updateSim;
    bool printStats;
    bool pauseSim;
    double lastFrameTime;

    CircleRenderer* renderer;
} gDisplay;

// renderPicture --
void renderPicture() {
    double startTime = CycleTimer::currentSeconds();

    // clear screen
    gDisplay.renderer->clearImage();
    double endClearTime = CycleTimer::currentSeconds();

    // update particle positions and state
    if (gDisplay.updateSim) {
        gDisplay.renderer->advanceAnimation();
    }
    if (gDisplay.pauseSim)
        gDisplay.updateSim = false;

    double endSimTime = CycleTimer::currentSeconds();

    // render the particles into the image
    gDisplay.renderer->render();

    double endRenderTime = CycleTimer::currentSeconds();

    if (gDisplay.printStats) {
        printf("Clear:    %.3f ms\n", 1000.f * (endClearTime - startTime));
        printf("Advance:  %.3f ms\n", 1000.f * (endSimTime - endClearTime));
        printf("Render:   %.3f ms\n", 1000.f * (endRenderTime - endSimTime));
    }
}

// Save the rendered image to a PPM file
void saveRenderedImage(const char* filename) {
    const Image* img = gDisplay.renderer->getImage();
    FILE* file = fopen(filename, "wb");
    if (!file) {
        fprintf(stderr, "Error opening file: %s\n", filename);
        return;
    }
    
    // Write PPM header
    fprintf(file, "P6\n%d %d\n255\n", img->width, img->height);
    
    // Write image data
    for (int i = 0; i < img->width * img->height; i++) {
        unsigned char r = (unsigned char)(255.0f * img->data[4*i]);
        unsigned char g = (unsigned char)(255.0f * img->data[4*i+1]);
        unsigned char b = (unsigned char)(255.0f * img->data[4*i+2]);
        fputc(r, file);
        fputc(g, file);
        fputc(b, file);
    }
    
    fclose(file);
    printf("Image saved to %s\n", filename);
}

void startRendererWithDisplay(CircleRenderer* renderer) {
    // setup the display
    const Image* img = renderer->getImage();

    gDisplay.renderer = renderer;
    gDisplay.updateSim = true;
    gDisplay.pauseSim = false;
    gDisplay.printStats = true;
    gDisplay.lastFrameTime = CycleTimer::currentSeconds();
    gDisplay.width = img->width;
    gDisplay.height = img->height;

    printf("Starting headless renderer\n");
    
    // Render a fixed number of frames
    for (int i = 0; i < 20; i++) {
        printf("Rendering frame %d\n", i+1);
        renderPicture();
        
        // Save the last frame
        if (i == 19) {
            saveRenderedImage("output.ppm");
        }
        
        gDisplay.lastFrameTime = CycleTimer::currentSeconds();
    }
}

#else
// Original OpenGL version (include your original display.cpp code here)
#include "platformgl.h"

void renderPicture();

static struct {
    int width;
    int height;
    bool updateSim;
    bool printStats;
    bool pauseSim;
    double lastFrameTime;

    CircleRenderer* renderer;
} gDisplay;

// handleReshape --
//
// Event handler, fired when the window is resized
void
handleReshape(int w, int h) {
    gDisplay.width = w;
    gDisplay.height = h;
    glViewport(0, 0, gDisplay.width, gDisplay.height);
    glutPostRedisplay();
}

void
handleDisplay() {
    // simulation and rendering work is done in the renderPicture
    // function below
    renderPicture();

    // the subsequent code uses OpenGL to present the state of the
    // rendered image on the screen.
    const Image* img = gDisplay.renderer->getImage();

    int width = std::min(img->width, gDisplay.width);
    int height = std::min(img->height, gDisplay.height);

    glDisable(GL_DEPTH_TEST);
    glClearColor(0.f, 0.f, 0.f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0.f, gDisplay.width, 0.f, gDisplay.height, -1.f, 1.f);

    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // copy image data from the renderer to the OpenGL
    // frame-buffer.  This is inefficient solution is the processing
    // to generate the image is done in CUDA.  An improved solution
    // would render to a CUDA surface object (stored in GPU memory),
    // and then bind this surface as a texture enabling it's use in
    // normal openGL rendering
    glRasterPos2i(0, 0);
    glDrawPixels(width, height, GL_RGBA, GL_FLOAT, img->data);

    double currentTime = CycleTimer::currentSeconds();

    if (gDisplay.printStats)
        printf("%.2f ms\n", 1000.f * (currentTime - gDisplay.lastFrameTime));

    gDisplay.lastFrameTime = currentTime;

    glutSwapBuffers();
    glutPostRedisplay();
}

// handleKeyPress --
//
// Keyboard event handler
void
handleKeyPress(unsigned char key, int x, int y) {
    switch (key) {
    case 'q':
    case 'Q':
        exit(1);
        break;
    case '=':
    case '+':
        gDisplay.updateSim = true;
        break;
    case 'p':
    case 'P':
        gDisplay.pauseSim = !gDisplay.pauseSim;
        if (!gDisplay.pauseSim)
            gDisplay.updateSim = true;
        break;
    }
}

// renderPicture --
//
// At the reall work is done here, not in the display handler
void
renderPicture() {
    double startTime = CycleTimer::currentSeconds();

    // clear screen
    gDisplay.renderer->clearImage();
    double endClearTime = CycleTimer::currentSeconds();

    // update particle positions and state
    if (gDisplay.updateSim) {
        gDisplay.renderer->advanceAnimation();
    }
    if (gDisplay.pauseSim)
        gDisplay.updateSim = false;

    double endSimTime = CycleTimer::currentSeconds();

    // render the particles< into the image
    gDisplay.renderer->render();

    double endRenderTime = CycleTimer::currentSeconds();

    if (gDisplay.printStats) {
        printf("Clear:    %.3f ms\n", 1000.f * (endClearTime - startTime));
        printf("Advance:  %.3f ms\n", 1000.f * (endSimTime - endClearTime));
        printf("Render:   %.3f ms\n", 1000.f * (endRenderTime - endSimTime));
    }
}

void
startRendererWithDisplay(CircleRenderer* renderer) {
    // setup the display
    const Image* img = renderer->getImage();

    gDisplay.renderer = renderer;
    gDisplay.updateSim = true;
    gDisplay.pauseSim = false;
    gDisplay.printStats = true;
    gDisplay.lastFrameTime = CycleTimer::currentSeconds();
    gDisplay.width = img->width;
    gDisplay.height = img->height;

    // configure GLUT
    glutInitWindowSize(gDisplay.width, gDisplay.height);
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE);
    glutCreateWindow("CMU 15-418 Assignment 2 - Circle Renderer");
    glutDisplayFunc(handleDisplay);
    glutKeyboardFunc(handleKeyPress);
    glutMainLoop();
}
#endif