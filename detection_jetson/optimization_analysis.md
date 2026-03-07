## Ways to improve FPS

### Choose MAXN power mode
```sudo nvpmodel -m 2```

### Lock clocks to a maximum of a current power mode
```sudo jetson_clocks --store```
(Revert with --restore flag)

### Compile model with batching

### Try SAHI library for slicing

### Compile model to TensorRT

### Compile model with FP16 weights