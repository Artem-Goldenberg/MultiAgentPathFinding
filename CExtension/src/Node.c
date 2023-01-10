#include "Node.h"
#include <stdlib.h>

static int cantor(int a, int b) {
    return (a + b + 1) * (a + b) / 2 + b;
}

static int hash(Node *node, int numBuckets) {
    int a = node->p.x, b = node->p.y, t = node->g;
    return abs(cantor(a, cantor(b, t))) % numBuckets;
}

static int cmp(Node *node1, Node *node2) {
    int dt = node1->g - node2->g;
    if (dt != 0) return dt;
    return pointCmp(node1->p, node2->p);
}

int nodeHash(const void *p, int numBuckets) {
    return hash((Node*)p, numBuckets);
}

int nodeCmp(const void *p1, const void *p2) {
    return cmp((Node*)p1, (Node*)p2);
}

int nodePtrHash(const void *p, int numBuckets) {
    return hash(*(Node**)p, numBuckets);
}

int nodePtrCmp(const void *p1, const void *p2) {
    return cmp(*(Node**)p1, *(Node**)p2);
}

int mddNodeHash(const void *p, int numBuckets) {
    // since head of `MddNode` is the same as in `Node`
    // we can just cast the pointer as a pointer to `Node`
    return hash(*(Node**)p, numBuckets);
}

int mddNodeCmp(const void *p1, const void *p2) {
    return cmp(*(Node**)p1, *(Node**)p2);
}

void addParent(MddNode *node, MddNode *parent) {
    int i = 0;
    while (node->parents[i]) ++i; // skip to an empty slot
    node->parents[i] = parent;
}