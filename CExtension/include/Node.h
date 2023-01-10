#ifndef Node_h
#define Node_h

#include "Map.h"

typedef struct Node {
    Point p;
    int g, f;
    struct Node* parent;
} Node;

int nodeHash(const void *p, int numBuckets);
int nodeCmp(const void *p1, const void *p2);

int nodePtrHash(const void *p, int numBuckets);
int nodePtrCmp(const void *p1, const void *p2);

typedef struct MddNode {
    Point p;
    int g, f;
    struct MddNode *parents[5];
} MddNode;

int mddNodeHash(const void *p, int numBuckets);
int mddNodeCmp(const void *p1, const void *p2);

void addParent(MddNode *node, MddNode *parent);

#endif /* Node_h */
