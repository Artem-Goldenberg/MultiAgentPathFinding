#include "Algorithm.h"

#include "Set.h"
#include "Allocator.h"
#include "PriorityQueue.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NUM_BUCKETS 1337

int manhattan(Point p1, Point p2) {
    return abs(p1.x - p2.x) + abs(p1.y - p2.y);
}

static int lowestG(const void *p1, const void *p2) {
    Node *node1 = (Node*)p1, *node2 = (Node*)p2;
    // reverse order, lower f, higher priority
    int df = node2->f - node1->f;
    if (df != 0) return df;
    // reverse order, lower g, higher priority
    return node2->g - node1->g;
}

static int highestG(const void *p1, const void *p2) {
    Node *node1 = (Node*)p1, *node2 = (Node*)p2;
    // reverse order, lower f, higher priority
    int df = node2->f - node1->f; 
    if (df != 0) return df;
    // same order here, higher g, higher priority
    return node1->g - node2->g;
}

Allocator *a;

bool findPath(Map *map, Point s, Point g, Node *storage) {
    Set *closed = newSet(sizeof(Node*), NUM_BUCKETS, nodePtrHash, nodePtrCmp, NULL);
    PriorityQueue *open = newQueue(sizeof(Node), map->height * map->width / 2, highestG);
    
    int maxConstrainedTime = getGoalTimeBoundary(map, g);
    bool found = false;
    bool isGoal = false;

    Node *node = allocate(a, sizeof(Node));
    memset(node, 0, sizeof(Node));
    node->p = s;
    enqueue(open, node);
    
    while (dequeue(open, node)) {
        isGoal = false;
        if (node->p.x == g.x && node->p.y == g.y) {
            isGoal = true;
            if (node->g > maxConstrainedTime) {
                found = true;
                *storage = *node;
                break;
            }
        }

        if (searchSet(closed, &node) != NULL)
            // duplicate node, was already expanded
            continue;
        
        addTo(closed, &node);
        
        Point neighbors[5];
        int amount = getNeighbors(map, node->g + 1, node->p, isGoal, neighbors);
        for (int i = 0; i < amount; ++i) {
            Node neighbour = {neighbors[i], .g = node->g + 1};
            Node *ptr = &neighbour;

            if (searchSet(closed, &ptr) == NULL) {
                neighbour.f = neighbour.g + manhattan(neighbour.p, g);
                neighbour.parent = node;
                enqueue(open, &neighbour);
            }
        }
        node = allocate(a, sizeof(Node));
    }
    
    deleteQueue(open);
    deleteSet(closed);
    
    return found;
}

bool findAllPaths(Map *map, Point s, Point g, MddNode *storage) {
    Set *closed = newSet(sizeof(MddNode*), NUM_BUCKETS, nodePtrHash, nodePtrCmp, NULL);
    
    // can use the same `highestG` and `lowestG` functions because `MddNode` stores data in the same way
    PriorityQueue *open = newQueue(sizeof(MddNode), map->height * map->width / 2, lowestG);
    
    int maxConstrainedTime = getGoalTimeBoundary(map, g);
    bool found = false;
    bool isGoal = false;
    
    MddNode *node = allocate(a, sizeof(MddNode));
    memset(node, 0, sizeof(MddNode));
    node->p = s;
    enqueue(open, node);
    
    while (dequeue(open, node)) {
        isGoal = false;
        if (pointCmp(node->p, g) == 0) {
            isGoal = true;
            if (node->g > maxConstrainedTime) {
                found = true;
                *storage = *node;
                break;
            }
        }
        
        MddNode **expanded = searchSet(closed, &node);
        if (expanded) {
            // found duplicate, add to parents and skip
            addParent(*expanded, node->parents[0]);
            continue;
        }
        
        addTo(closed, &node);
        
        Point neighbors[5];
        int amount = getNeighbors(map, node->g + 1, node->p, isGoal, neighbors);
        for (int i = 0; i < amount; ++i) {
            MddNode neighbour = {neighbors[i], .g = node->g + 1};
            MddNode *ptr = &neighbour;

            if (searchSet(closed, &ptr) == NULL) {
                neighbour.f = neighbour.g + manhattan(neighbour.p, g);
                addParent(&neighbour, node);
                enqueue(open, &neighbour);
            }
        }
        node = allocate(a, sizeof(MddNode));
    }
    
    while (dequeue(open, node) && pointCmp(node->p, storage->p) == 0)
        addParent(storage, node->parents[0]);
    
    deleteQueue(open);
    deleteSet(closed);
    
    return found;
}

bool testPath(void) {
    // specify actual map
    // 1 - wall, 0 - path
    const char mapArray[] = {
        1, 0, 0, 0, 0, 0, 1,
        1, 0, 0, 1, 1, 0, 1,
        1, 0, 0, 1, 1, 1, 1,
        1, 1, 0, 0, 0, 0, 1,
        1, 1, 1, 1, 1, 1, 1
    };
    
    int mapWidth = 7;
    int mapHeight = 5;
    
    Point start = {1, 0};     // <----- specify start point (x, y)
    Point goal = {1, 1};     // <------- specify goal point (x, y)
    
    a = newAllocator(10, mapWidth * mapHeight / 2);
    
    Array vConstraints, eConstraints;
    
    // specify constraints
    VConstraint vConstraintsArray[] = {
        {1, {1, 0}}, // at t = 1, cannot be at (1, 0)
        {1, {3, 3}}, // at t = 1, cannot also be at (3, 3)
        {2, {3, 1}}, // at t = 2, cannot bet at (3, 1)
        // etc...
    };
    
    // specify constraints
    EConstraint eConstraintsArray[] = {
        {1, { {0, 0}, {0, 1} }}, // at t = 1, cannot go by edge (0, 0) -> (0, 1)
        {0, { {1, 0}, {1, 1} }}, // at t = 0, cannot go (1, 0) -> (1, 1) or (1, 1) -> (1, 0) it is the same
        // etc...
    };
    
    initArrayWithBuffer(&vConstraints,
                        sizeof(VConstraint),
                        vConstraintsArray,
                        sizeof(vConstraintsArray) / sizeof(VConstraint));
    
    initArrayWithBuffer(&eConstraints,
                        sizeof(EConstraint),
                        eConstraintsArray,
                        sizeof(eConstraintsArray) / sizeof(EConstraint));
    
    Map *map = newMapWithConstraints(mapWidth, mapHeight, &vConstraints, &eConstraints, mapArray);
    // if vConstraints or eConstraints is empty here ----->^^^^^^^^^^^^^^^^^^^^^^^^^, better pass NULL instead of
    // empty constraints
    // say eConstraints is empty, then
//    Map *map = newMapWithConstraints(mapWidth, mapHeight, &vConstraints, NULL, mapArray);
    // ^^^^^^^^^^ this would be the call                                   ^^^^
    
    Node result;
    bool found = findPath(map, start, goal, &result);
    
    if (!found) {
        deleteAllocator(a);
        return false;
    }

    int l = 0;
    Point path[100] = {0};
    Node *current = &result;
    printf("result.g = %d\n", result.g);
    while (current) {
        path[l++] = current->p;
        printf("(%d, %d) <- ", current->p.x, current->p.y);
        current = current->parent;
    }
    printf("\n");

    deleteAllocator(a);
    deleteMap(map);
    
    return found;
}

// int main() { 
//     // testPath();
//     printf("some");
//     return 0;
// }
