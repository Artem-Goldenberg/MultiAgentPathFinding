#ifndef Array_h
#define Array_h

#include "GenericFunctions.h"
#include <stddef.h>
#include <stdbool.h>

#define ARRAY_NOT_FOUND -1

typedef struct {
    void *data;
    int width;
    int count;
    int capacity;
    FreeFunction freefn;
} Array;

void initArray(Array *atPointer, size_t withElementsOfSize, size_t capacity, FreeFunction usingFreeFunction);
void initArrayWithBuffer(Array *atPointer, size_t withElementsOfSize, void *bytesBuffer, size_t elementsAmount);

Array *newArray(size_t withElementsOfSize, size_t capacity, FreeFunction usingFreeFunction);
Array *newArrayWithBuffer(size_t withElementsOfSize, void *bytesBuffer, size_t elementsAmount);

int countArray(Array *theArray);
void *getElement(Array *ofArray, int atIndex);

void append(Array *array, const void *withElementFromAddress);
void insert(Array *intoArray, const void *fromAddress, int atIndex);
void pop(Array *array, int atIndex);

void mapArray(Array *array, MapFunction withMapping, void *usingAdditionalData);
void clearArray(Array *array);

int searchArray(Array *array, const void *forElementAtAddress, CompareFunction usingOrderFunction, bool isSorted);
void sortArray(Array *array, CompareFunction usingOrderFunction);

void deinitArray(Array *array);
void deleteArray(Array *array);

#endif /* Array_h */
