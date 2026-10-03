# Maintenance

When Scale changes:
1. identify the routing/architecture failure or stale assumption;
2. edit the smallest authoritative layer;
3. preserve the Scale/Governor boundary;
4. validate `assets/execution-contract.json`;
5. run static Skill audit and regression tests;
6. recheck current model/surface facts when they affect routing;
7. record material changes in Git history.

Do not introduce universal numeric complexity scores or fixed model rankings without calibration evidence.
