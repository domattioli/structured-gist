```text
- Library boundary ▸ First library ↪ generates a triangular mesh from a 2D domain description, porting locked numerical stages that stay bit-identical to the reference MATLAB implementation ▸ Second library a. general-purpose mesh data structure b. smoothing operations c. quality analysis d. triangle-to-quad conversion ▸ Composition ↪ the first library's output format round-trips cleanly into the second library's loader
```
