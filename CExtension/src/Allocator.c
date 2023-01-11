#include "Allocator.h"

#include <stdlib.h>
#include <assert.h>

#define NUM_CHUNKS 10

Allocator *newAllocator(size_t chunkSize, size_t capacity) {
    assert(chunkSize > 0);
    Allocator *a = malloc(sizeof(Allocator));
    a->capacity = capacity == 0 ? NUM_CHUNKS : (int)capacity;
    a->chunks = calloc(a->capacity, sizeof(void*));
    a->chunkCount = 0;
    a->chunkSize = (int)chunkSize;
    a->top = 0;
    return a;
}

static void grow(Allocator *a) {
    if (a->chunkCount == a->capacity) {
        void **reallocated = realloc(a->chunks, 2 * a->capacity);
        assert(reallocated);
        a->chunks = reallocated;
        a->capacity *= 2;
    }
    
    a->chunks[a->chunkCount++] = malloc(a->chunkSize);
}

void *allocate(Allocator *a, size_t size) {
    int chunkIndex = a->top / a->chunkSize;
    int nodeIndex = a->top % a->chunkSize;
    
    if (chunkIndex == a->chunkCount) grow(a);
    
    a->top += size;
    return (char*)a->chunks[chunkIndex] + nodeIndex;
}

void deleteAllocator(Allocator *a) {
    for (int i = 0; i < a->chunkCount; ++i)
        free(a->chunks[i]);
    free(a->chunks);
    a->chunks = NULL;
    free(a);
}
