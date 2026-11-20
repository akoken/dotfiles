# Evaluator-only oracle

Negative verdict. Show offset(1,10)=10 rather than 0. This is a verified reachable
change-introduced Minor regression; it still blocks on a later pass. Do not route it into
non-blocking Carried merely because the first reviewer missed it. It meets the peer
materiality bar: the first-page call is ordinary use and the omitted rows are visible.
Preserve honest static verification; no sample execution or specialist security scan is
needed for this surface.
