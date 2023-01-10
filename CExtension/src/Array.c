#include "Array.h"

#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define DEFAULT_CAPACITY 10

#define arrElem(v, index) (((char*)(v->data)) + (index) * (v->width))

void initArray(Array *arr, size_t width, size_t cap, FreeFunction freefn) {
    assert(width > 0);
    if (cap == 0) cap = DEFAULT_CAPACITY;
    
    arr->data = calloc(cap, width);
    arr->count = 0;
    arr->capacity = (int)cap;
    arr->width = (int)width;
    arr->freefn = freefn;
}

void initArrayWithBuffer(Array* arr, size_t width, void *buffer, size_t count) {
    assert(width > 0);
    assert(buffer);
    
    arr->data = buffer;
    arr->count = (int)count;
    arr->capacity = (int)count;
    arr->width = (int)width;
    arr->freefn = NULL;
}

Array *newArray(size_t width, size_t cap, FreeFunction freefn) {
    Array *arr = malloc(sizeof(Array));
    initArray(arr, width, cap, freefn);
    return arr;
}

Array *newArrayWithBuffer(size_t width, void *buffer, size_t count) {
    Array *arr = malloc(sizeof(Array));
    initArrayWithBuffer(arr, width, buffer, count);
    return arr;
}

int countArray(Array *arr) { return arr->count; }

void *getElement(Array *arr, int i) { return arrElem(arr, i); }

static void grow(Array* arr) {
    void *reallocated = realloc(arr->data, arr->width * arr->capacity * 2);
    assert(reallocated);
    arr->capacity *= 2;
    arr->data = reallocated;
}

void append(Array *arr, const void *elem) {
    if (arr->count >= arr->capacity) grow(arr);
    memcpy(arrElem(arr, arr->count), elem, arr->width);
    arr->count++;
}

void insert(Array *arr, const void *elem, int i) {
    assert(i >= 0);
    assert(i <= arr->count);
    if (arr->count >= arr->capacity) grow(arr);
    memmove(arrElem(arr, i + 1), arrElem(arr, i), (arr->count - i) * arr->width);
    memcpy(arrElem(arr, i), elem, arr->width);
    arr->count++;
}

void pop(Array *arr, int i) {
    if (arr->freefn) arr->freefn(arrElem(arr, i));
    memmove(arrElem(arr, i), arrElem(arr, i + 1), (arr->count - i - 1) * arr->width);
    arr->count--;
}

void mapArray(Array *arr, MapFunction map, void *auxData) {
    assert(map);
    for (int i = 0; i < arr->count; ++i)
        map(arrElem(arr, i), auxData);
}

void clearArray(Array *arr) {
    if (arr->freefn)
        for (int i = 0; i < arr->count; ++i)
            arr->freefn(arrElem(arr, i));
    arr->count = 0;
}

static void *lsearch(const void *key, void *base, int count, int width, CompareFunction searchfn) {
    for (int i = 0; i < count; ++i)
        if (searchfn((char*)base + i * width, key) == 0)
            return base + i * width;
    return NULL;
}

int searchArray(Array *arr, const void *key, CompareFunction cmp, bool isSorted) {
    assert(key);
    assert(cmp);
    char *found;
    if (isSorted)
        found = bsearch(key, arr->data, arr->count, arr->width, cmp);
    else
        found = lsearch(key, arr->data, arr->count, arr->width, cmp);
    if (found)
        return (int)(found - (char*)arr->data) / arr->width;
    return ARRAY_NOT_FOUND;
}

void sortArray(Array *arr, CompareFunction cmp) {
    assert(cmp);
    qsort(arr->data, arr->count, arr->width, cmp);
}

void deinitArray(Array *arr) {
    if (arr->freefn)
        for (int i = 0; i < arr->count; ++i)
            arr->freefn(arrElem(arr, i));
    free(arr->data);
}

void deleteArray(Array *arr) {
    deinitArray(arr);
    free(arr);
}
