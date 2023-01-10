#ifndef PriorityQueue_h
#define PriorityQueue_h

#include "GenericFunctions.h"

#include <stddef.h>
#include <stdbool.h>

/** Stores the element in the order defined by cmp function
 Do not interact with fields directly, only use through the functions below
 Create only using `newQueue` function, when created, must be deleted with `deleteQueue`
 */
typedef struct {
    void* nodes;
    size_t width;
    size_t size;
    size_t capacity;
    CompareFunction cmp;
} PriorityQueue;

/// Creates new queue
/// `width` - size of the elements (in bytes) in the queue
/// `capacity` - pre-allocated number of elements
/// `cmp` - comparator of priorities of two elements
PriorityQueue *newQueue(size_t width, size_t capacity, CompareFunction priorityComparator);

/// Draw element with the HIGHEST priority (as cmp function is concerned) from the `q`
/// Element will be copied at the provided `storage` pointer
/// `storage` cannot be `NULL` and must have sufficient space
bool dequeue(PriorityQueue *q, void *storage);

/// Insert element pointed by `node` in the queue
void enqueue(PriorityQueue *q, const void *node);

/// Deleted the queue and frees all allocated space
void deleteQueue(PriorityQueue *q);

#endif /* PriorityQueue_h */
