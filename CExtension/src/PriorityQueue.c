#include "PriorityQueue.h"

#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define getElem(q, i) (char*)q->nodes + q->width * (i)

PriorityQueue *newQueue(size_t width, size_t capacity, CompareFunction cmp) {
    assert(capacity > 0);
    PriorityQueue *q = malloc(sizeof(PriorityQueue));
    q->nodes = calloc(capacity, width);
    q->capacity = capacity;
    q->width = width;
    q->size = 0;
    q->cmp = cmp;
    return q;
}

bool dequeue(PriorityQueue *q, void *storage) {
    assert(storage);
    if (q->size == 0) return false;
    q->size--;
    memcpy(storage, getElem(q, q->size), q->width);
    return true;
}

static void grow(PriorityQueue *q) {
    void *reallocated = realloc(q->nodes, q->width * q->capacity * 2);
    assert(reallocated);
    q->capacity *= 2;
    q->nodes = reallocated;
}

static int binarySearch(PriorityQueue *q, const void *target) {
    int a = 0, b = (int)q->size, m;
    do {
        m = (a + b) / 2;
        int cmp = q->cmp(getElem(q, m), target);
        if (cmp < 0) a = m + 1;
        else if (cmp > 0) b = m;
        else break;
        m = a;
    } while (a != b);
    
    // we want to insert equal value to the rightmost index
    // so it will be extracted first
    while (m < b && q->cmp(getElem(q, m), target) == 0) ++m;
    // no, we don't
    // yes we do
    
    return m;
}

void enqueue(PriorityQueue *q, const void *node) {
    if (q->size == q->capacity) grow(q);
    
    if (q->size == 0) {
        memcpy(getElem(q, q->size), node, q->width);
        q->size++;
        return;
    }
    
    int paste = binarySearch(q, node);
    
    memmove(getElem(q, paste + 1), getElem(q, paste), q->width * (q->size - paste));
    memcpy(getElem(q, paste), node, q->width);
    
    q->size++;
}

void deleteQueue(PriorityQueue *q) {
    free(q->nodes);
    free(q);
}
