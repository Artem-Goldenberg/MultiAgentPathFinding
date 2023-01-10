#ifndef Allocator_h
#define Allocator_h

#include <stddef.h>

/** Allocates memory in chunks of a specified size
 If more memory needed, it will add more and more chunks to allocate in
 Do not interact with fields directly, only use through the functions below
 Create only using `newAllocator` function, when created, must be deleted with `deleteAllocator`
 After creating use `allocate` to get acces to the new memory
 */
typedef struct {
    void **chunks;
    int capacity;
    int chunkCount;
    int chunkSize;
    int top;
} Allocator;


/// Creates new allocator with given nonzero `chunkSize` (in bytes) and capacity
/// `expectedChunkCount` is the amount of chunks which will be pre-allocated
///  if set to `0` allocated default amount of chunks.
Allocator *newAllocator(size_t chunkSize, size_t expectedChunkCount);

/// Allocates space of given `size` (in bytes)
/// Returns a pointer at the start of the allocated region
void *allocate(Allocator *a, size_t size);

///Remove the allocator and free all allocated space
void deleteAllocator(Allocator *a);

#endif /* Allocator_h */
