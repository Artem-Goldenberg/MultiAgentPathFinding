#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

#include "Set.h"
#include "Map.h"
#include "Allocator.h"
#include "Algorithm.h"

#define NUM_BUCKETS 317

/// Uncomment if you want to debug `A*`
// #define DebugMode


extern Allocator *a;

static Map *setupConstraints(PyArrayObject *grid, PyArrayObject *vConstraints, PyArrayObject *eConstraints) {
    int vConstraintsCount = 0;
    if (vConstraints) vConstraintsCount = (int)PyArray_DIM(vConstraints, 0);

    int eConstraintsCount = 0;
    if (eConstraints) eConstraintsCount = (int)PyArray_DIM(eConstraints, 0);

    int w = (int)PyArray_DIM(grid, 1);
    int h = (int)PyArray_DIM(grid, 0);
    char *mapBytes = PyArray_BYTES(grid);

    if (vConstraintsCount > 0 || eConstraintsCount > 0) {
        Array constraints[2] = {0};
        Array *vc = NULL, *ec = NULL;
        if (vConstraintsCount > 0) {
            initArrayWithBuffer(constraints, sizeof(VConstraint), PyArray_DATA(vConstraints), vConstraintsCount);
            vc = constraints;
        }
        if (eConstraintsCount > 0)  {
            initArrayWithBuffer(constraints + 1, sizeof(EConstraint), PyArray_DATA(eConstraints), eConstraintsCount);
            ec = constraints + 1;
        }
        return newMapWithConstraints(w, h, vc, ec, mapBytes);
    }
    return newMap(w, h, mapBytes);
}

static void logConstraints(PyArrayObject *vConstraints, PyArrayObject *eConstraints) {
    int vConstraintsCount = 0;
    if (vConstraints) vConstraintsCount = (int)PyArray_DIM(vConstraints, 0);

    int eConstraintsCount = 0;
    if (eConstraints) eConstraintsCount = (int)PyArray_DIM(eConstraints, 0);
    
    printf("VertexConstraints: len = %d ", vConstraintsCount);
    puts("in format: t, (x, y)");

    VConstraint *vcs = (VConstraint*)PyArray_DATA(vConstraints);
    for (int i = 0; i < vConstraintsCount; ++i)
        printf("[%d] = %d, (%d, %d)\n", i, vcs[i].time, vcs[i].p.x, vcs[i].p.y);
    
    printf("\nEdgeConstraints: len = %d ", eConstraintsCount);
    puts("in format: t, (x1, y1) -> (x2, y2)");
    
    EConstraint *ecs = (EConstraint*)PyArray_DATA(eConstraints);
    for (int i = 0; i < eConstraintsCount; ++i)
        printf("[%d] = %d, (%d, %d) -> (%d, %d)\n",
               i, ecs[i].time, ecs[i].e.p1.x, ecs[i].e.p1.y, ecs[i].e.p2.x, ecs[i].e.p2.y);
    
    printf("\n");
}

static PyArrayObject *constructPath(Node *result) {
    // create the return array
    npy_intp shape[] = {result->g + 1, 2};
    PyArrayObject *path = (PyArrayObject*)PyArray_SimpleNew(2, shape, NPY_INT);
    
    // fill the array by unwinding the path by traveling through `parent`
    Point *p = PyArray_DATA(path);
    p += result->g;
    Node *current = result;
#ifdef DebugMode
    printf("found path with length = %d\n", result->g);
#endif
    while (current) {
        *p = current->p;
        --p;
#ifdef DebugMode
        printf("(%d, %d) <- ", current->p.x, current->p.y);
#endif
        current = current->parent;
    }
#ifdef DebugMode
    printf("\n\n");
#endif
    
    return path;
}

static void fillArray(void *p, void *auxData) { 
    MddNode *node = *(MddNode**)p;
    Point **ptr = (Point**)auxData;
    **ptr = node->p;
    (*ptr)++;
}

typedef struct {
    Set *nextLayer;
    int *ptr;
} MapHelper;

static void appendParents(void *p, void *auxData) {
    MddNode *node = *(MddNode**)p;
    MapHelper *helper = (MapHelper*)auxData;
    
    for (int i = 0; i < 5 && node->parents[i]; ++i) {
        addTo(helper->nextLayer, &node->parents[i]);
        helper->ptr[-1]++; // increase number of edges
    }
    
    helper->ptr[0]++; // increase number of nodes
}

static PyObject *constructPathAndMdd(MddNode *result, bool liteMdd, bool fullMdd) {
    PyArrayObject *path = constructPath((Node*)result);

    npy_intp shape[] = {result->g * 2 + 1};
    PyArrayObject *countedMdd = liteMdd ? (PyArrayObject*)PyArray_ZEROS(1, shape, NPY_INT, 0) : NULL;
    int *countedMddPtr = liteMdd ? PyArray_DATA(countedMdd) : NULL;

    PyListObject *mdd = fullMdd ? (PyListObject*)PyList_New(result->g + 1) : NULL;
    
    Set layers[2];
    Set *layer = layers, *nextLayer = layers + 1;
    initSet(layer, sizeof(MddNode*), NUM_BUCKETS, mddNodeHash, mddNodeCmp, NULL);
    initSet(nextLayer, sizeof(MddNode*), NUM_BUCKETS, mddNodeHash, mddNodeCmp, NULL);

    addTo(layer, &result);
    for (int i = 0; i <= result->g; ++i) {
        int *ptr;
        if (liteMdd) {
            ptr = countedMddPtr + (result->g - i) * 2;
        } else {
            int dummy[] = {0, 0};
            ptr = dummy + 1;
        }
        MapHelper helper = {nextLayer, ptr};
        mapSet(layer, appendParents, &helper);

        if (fullMdd) { 
            npy_intp shape[] = {ptr[0], 2};
            PyArrayObject *mddLayer = (PyArrayObject*)PyArray_SimpleNew(2, shape, NPY_INT);
            Point *p = PyArray_DATA(mddLayer);
            mapSet(layer, fillArray, &p);
            PyList_SET_ITEM(mdd, i, (PyObject*)mddLayer);
        }
        
        // swap layers and clear nextLayer
        Set *tmp = layer;
        layer = nextLayer;
        nextLayer = tmp;
        clearSet(nextLayer);
    }

    if (fullMdd) PyList_Reverse((PyObject*)mdd);
    
    deinitSet(layer);
    deinitSet(nextLayer);
    
    if (liteMdd && fullMdd) 
        return PyTuple_Pack(3, path, countedMdd, mdd);
    else if (fullMdd) // only full mdd
        return PyTuple_Pack(2, path, mdd);
    else // only lite mdd
        return PyTuple_Pack(2, path, countedMdd);
}

static PyObject *
fromPython(PyObject *self, PyObject *args, PyObject *keywords)
{
    PyArrayObject *grid = NULL, *vConstraints = NULL, *eConstraints = NULL;
    int sx, sy, gx, gy;
    bool liteMdd = false, fullMdd = false;
    static char *keylist[] = {"map", "start", "goal", "v_constraints", "e_constraints", "lite_mdd", "full_mdd", NULL};

    if (!PyArg_ParseTupleAndKeywords(
        args, keywords, "O!(ii)(ii)|O!O!ii", keylist, 
        &PyArray_Type, &grid, 
        &sx, &sy, &gx, &gy, 
        &PyArray_Type, &vConstraints, 
        &PyArray_Type, &eConstraints,
        &liteMdd, &fullMdd
    ))
        return NULL;

    Map *map = setupConstraints(grid, vConstraints, eConstraints);

#ifdef DebugMode
    puts("\n----------------------------------------------");
    printf("Calculating path from (%d, %d) to (%d, %d)\n\n", sx, sy, gx, gy);
    logConstraints(vConstraints, eConstraints);
#endif
    
    Point s = {sx, sy}, g = {gx, gy};
    
#ifdef DebugMode
    printf("minimum path lenght with respect to constraints = %d\n", getGoalTimeBoundary(map, g));
#endif

    bool found;
    PyObject *returnObject;
    if (!liteMdd && !fullMdd) {
        a = newAllocator(20 * sizeof(Node), map->width * map->height / 3);
        
        // actual A* here
        Node result;
        found = findPath(map, s, g, &result);
        if (found) returnObject = (PyObject*)constructPath(&result);
    } else {
        a = newAllocator(20 * sizeof(MddNode), map->width * map->height / 3);
        
        // A* for all paths
        MddNode result;
        found = findAllPaths(map, s, g, &result);
        printf("found is %d\n", found);
        if (found) returnObject = constructPathAndMdd(&result, liteMdd, fullMdd);
    }
    
    deleteMap(map);
    deleteAllocator(a);
    
    if (!found) {
#ifdef DebugMode
        puts("Path not found this time!");
        puts("Calculating is done");
        puts("----------------------------------------------\n");
#endif
        Py_RETURN_NONE;
    }

#ifdef DebugMode
    puts("Calculating is done");
    puts("----------------------------------------------\n");
#endif

    return returnObject;
}

static PyMethodDef methods[] = {
    {"find_path", (PyCFunction)(void(*)(void))fromPython, METH_VARARGS | METH_KEYWORDS,
     "Do some stuff"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef lightspeed = {
    PyModuleDef_HEAD_INIT,
    "lightspeed",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    methods
};

PyMODINIT_FUNC
PyInit_lightspeed(void)
{
    PyObject* mod = PyModule_Create(&lightspeed);
    import_array();
    return mod;
}
