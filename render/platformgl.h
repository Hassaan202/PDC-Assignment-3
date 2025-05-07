#ifndef __PLATFORM_GL_H__ 
#define __PLATFORM_GL_H__

#ifdef NO_OPENGL
// No GL includes needed for headless mode
#else
  #ifdef __APPLE__
  #include <GLUT/glut.h>
  #else
  #include <GL/glut.h>
  #endif
#endif

#endif