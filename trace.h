#ifndef H_TRACE
#define H_TRACE

#include "image_lib.h"
#include "contour_lib.h"
#include "seed.h"

#define FRAME_DELTA 1

#define HAT_RADIUS  1.5    //  Mexican-hat radius for whisker detection
#define MIN_LEVEL   1      //  Level-set threshold for an object
#define MIN_SIZE    20     //  Minimum # of pixels in an object

#define TLEN  8
#define OFFSET_STEP  .1   // pixels
#define ANGLE_STEP   18.  // divisions of pi/4
#define WIDTH_STEP   .2   // pixels [ngc: as of 2009-04-01 needs to be same as OFFSET_STEP]
#define MIN_SIGNAL   5.0  //  per column , typically: sigmin = (2*TLEN+1)*MIN_SIGNAL
#define MAX_DELTA_ANGLE  10.1 // degrees
#define MAX_DELTA_WIDTH   6.0 // pixels
#define MAX_DELTA_OFFSET  6.0 // pixels

#define DUPLICATE_THRESHOLD 5.0

#define HALF_SPACE_ASSYMETRY_THRESH 0.15     // between 0 and 1.  1 is completely insensitive to assymetry
//#define HALF_SPACE_FRACTION_DARK    0.2     // between 0 and 1.  Approximate fraction of dark area in image
//#define HALF_SPACE_TUNNELING_DECAY  0.99     // between 0 and 1.  Smaller values cause tunneling to stop sooner
#define HALF_SPACE_TUNNELING_MAX_MOVES 10   // pixels.  This should be the largest size of an occluding area to cross

typedef struct
  { int    cutoff;
    Image *mask;
  } Zone;

typedef struct
  { float  offset;
    float  angle;
    float  width;
    float  score;
  } Line_Params;

typedef struct
  { double min;
    double max;
  } Interval;

typedef struct
  { int    id;
    double width;
    int    beg;
    int    end;
    int    time;    /* in units of planes */
    float *track;
    float *scores;
  } Whisker_Seg_Old;

typedef struct
{ int id;
  int time;
  int len;
  float *x;
  float *y;
  float *thick;
  float *scores;
} Whisker_Seg;

typedef struct
{ void        **index;
  int          *sz;
  int           n;
} Index;

Whisker_Seg  *Make_Whisker_Seg              ( int n );
void          Free_Whisker_Seg              ( Whisker_Seg *w );
void          Free_Whisker_Seg_Vec          ( Whisker_Seg *wv, int n );

int           Compare_Whisker_Seg_Index     ( const void *a, const void *b );

Index        *Build_Whisker_Index           ( Whisker_Seg *wv, int n );
void          Free_Index                    ( Index *index );

//OLD void          write_whisk1_header           ( FILE *file );
//OLD void          write_whisk1_segment          ( FILE *file, Whisker_Seg *w );
//OLD void          write_segments                ( FILE *file, Whisker_Seg     **wv, int *sz, int nplanes );
//OLD void          write_segments_old            ( FILE* file, Whisker_Seg_Old **wv, int *sz, int nplanes );
//OLD Whisker_Seg  *Load_Whiskers_From_File       ( FILE *file, int *n);
//OLD Whisker_Seg  *Load_Whiskers                 ( char *filename, int *n);
//OLD int           Save_Whiskers                 ( char *filename, Whisker_Seg *wv, int n );
//void          Save_Whiskers                 ( char *filename, Index *whiskerindex );


Whisker_Seg  *find_segments                 (int iFrame, Image *image, Image *bg, int *nseg );
Image        *compute_background            (Stack *movie);
Zone         *compute_zone                  (Stack *movie);
float         eval_line                     (Line_Params *line, Image *image, int p);

int           adjust_line_walk              (Line_Params *line, Image *image, int *pp,
                                             Interval *roff, Interval *rang, Interval *rwid);

int           adjust_line_start             (Line_Params *line, Image *image, int *pp,
                                             Interval *roff, Interval *rang, Interval *rwid);

Whisker_Seg  *trace_whisker                 (Seed *s, Image *image);

#endif