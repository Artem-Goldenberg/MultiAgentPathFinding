#ifndef Algorithm_h
#define Algorithm_h

#include "Node.h"
#include <stdbool.h>

bool findPath(Map *map, Point s, Point g, Node *found);
    
// bool testPath(Map *map, Point s, Point g);

bool findAllPaths(Map *map, Point s, Point g, MddNode *found);

#endif /* Algorithm_h */
