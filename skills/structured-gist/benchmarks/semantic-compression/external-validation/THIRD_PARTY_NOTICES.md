# Third-party notices

This directory redistributes derived data from three public datasets. This
file is an attribution notice only; it is not legal advice, and it does not
claim to satisfy any license's requirements in full. Anyone redistributing
this corpus further should read each license's own text and reach their own
conclusion.

## HotpotQA

- **License**: CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
- **Source**: canonical `http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json`
  (unreachable at build time, TCP timeout); build fell back to the official
  mirror `https://huggingface.co/datasets/hotpotqa/hotpot_qa`, published by
  the same `hotpotqa` organization, pinned to HF repo sha
  `1908d6afbbead072334abe2965f91bd2709910ab`. See
  `scripts/fetch_sources.py` (`HOTPOTQA_ORIGINAL_URL`, `HOTPOTQA_HF_DATASET`,
  `fallback_source_publisher`) and `README.md`'s "One documented deviation."
- **Citation**: Yang, Z., Qi, P., Zhang, S., Bengio, Y., Cohen, W., Salakhutdinov,
  R., & Manning, C. D. (2018). HotpotQA: A Dataset for Diverse, Explainable
  Multi-hop Question Answering. In *Proceedings of the 2018 Conference on
  Empirical Methods in Natural Language Processing (EMNLP)*.
- **Modifications made**: 8 of 7,405 rows in the official `distractor` dev
  split were selected deterministically (bridge-type questions only, exactly
  2 supporting facts across exactly 2 distinct paragraphs, see README.md
  "HotpotQA (`pressure_only: true`)"). For each selected row, the build wrote
  a per-case directory containing the source text (`source.md`), a
  losslessly-preserved copy of the dataset's own question/answer/supporting
  facts (`external_gold.json`), a `provenance.json` record (upstream id,
  revision, license, retrieval date, content hashes, the host-fallback
  deviation), plus this project's own derived analysis files
  (`derived_gold.json`, `derived_blind_weights.json`, `coverage_audit.json`)
  built on top of that external data. A `selection.json` records the full
  eligibility pool and selection trace. `external_gold.json` and `source.md`
  reproduce upstream HotpotQA content; the other files are derived: see the share-alike note
  below for which files carry the derived-from-CC-BY-SA-4.0 obligation.

### Share-alike note (CC BY-SA 4.0)

CC BY-SA 4.0 requires that adaptations of licensed material be distributed
under the same or a compatible license. The following tracked files in this
repository are HotpotQA-derived and are distributed under CC BY-SA 4.0
(https://creativecommons.org/licenses/by-sa/4.0/):

- `hotpotqa/cases/hotpotqa-01/` through `hotpotqa/cases/hotpotqa-08/`, each
  containing `source.md`, `external_gold.json`, `provenance.json`,
  `derived_gold.json`, `derived_blind_weights.json`, and
  `coverage_audit.json` (confirmed via `git ls-files`: all six files exist
  under all eight `hotpotqa-0N` directories).
- `hotpotqa/selection.json` (tracked; confirmed via `git ls-files`).
- `calibration/hotpotqa-01/annotator_a.json`, `annotator_b.json`, and
  `calibration/hotpotqa-02/annotator_a.json`, `annotator_b.json` (confirmed
  via `git ls-files`), human-annotator calibration judgments recorded
  against HotpotQA-derived cases.

This is an attribution notice, not a legal determination of what CC BY-SA
4.0's share-alike clause does or does not require of the files above or of
downstream consumers of this repository.

## Qasper

- **License**: CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
- **Source**: official AllenAI tarball
  `https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz`
  (`qasper-train-dev-v0.3.tgz`, version `v0.3`), confirmed against the
  dataset's Hugging Face card (`cardData.license: cc-by-4.0`,
  https://huggingface.co/datasets/allenai/qasper) and homepage
  (https://allenai.org/data/qasper). See `scripts/fetch_sources.py`
  (`QASPER_TARBALL_URL`, `license_source`).
- **Citation**: Dasigi, P., Lo, K., Beltagy, I., Cohan, A., Smith, N. A., &
  Gardner, M. (2021). A Dataset of Information-Seeking Questions and Answers
  Anchored in Research Papers. In *Proceedings of the 2021 Conference of the
  North American Chapter of the Association for Computational Linguistics
  (NAACL)*.
- **Modifications made**: 10 of 788 eligible questions in the public
  `dev-v0.3` split were selected deterministically (7 multi-evidence + 3
  single-evidence, spread across paragraph-distance buckets, see README.md
  "Qasper" section). For each selected question, the build wrote a per-case
  directory (`qasper/cases/<case-id>/`) with `source.md` (paper text),
  `external_gold.json` (the dataset's own question, answer, and
  paragraph-level evidence, losslessly preserved), and `provenance.json`
  (upstream paper/question ids, revision, license, retrieval date, content
  hashes, the float-evidence caveat). `qasper/selection.json` records the
  eligibility pool and selection trace. Calibration files
  `calibration/qasper-01/` and `calibration/qasper-02/` (`annotator_a.json`,
  `annotator_b.json`) record human-annotator judgments against these cases.
  Note (per this repo's own baseline-code caveat in README.md): the
  `allenai/qasper-led-baseline` code repository is separately Apache-2.0;
  that is the *code's* license, not the dataset's, and is unrelated to this
  redistribution.

## QMSum

- **License**: MIT: https://opensource.org/license/mit
- **Source**: `github.com/Yale-LILY/QMSum`, pinned commit
  `83d7768c1f2b4dfeb091385d3dc7e239b8e5bb7e`. The build fetched the `LICENSE`
  file directly from that pinned commit and confirmed it reads "MIT
  License" (`scripts/fetch_sources.py::fetch_qmsum`,
  `QMSUM_LICENSE_URL = {QMSUM_RAW_BASE}/LICENSE`).
- **Citation**: Zhong, M., Yin, D., Yu, T., Zaidi, A., Mutuma, M., Jha, R.,
  Awadallah, A. H., Celikyilmaz, A., Liu, Y., Qiu, X., & Radev, D. (2021). QMSum: A New Benchmark for
  Query-based Multi-domain Meeting Summarization. In *Proceedings of the
  2021 Conference of the North American Chapter of the Association for
  Computational Linguistics (NAACL)*.
- **Modifications made**: 24 of 244 eligible specific-query candidates
  across the official `test` split of all three domains (Academic,
  Committee, Product) were selected deterministically (8 per domain, a
  12/12 single/multi split via a scarcity-first allocator, see README.md
  "QMSum" section). For each selected query, the build wrote a per-case
  directory (`qmsum/cases/<case-id>/`) with `source.md` (meeting
  transcript), `external_gold.json` (the dataset's own query, answer, and
  `relevant_text_span` evidence, losslessly preserved), and
  `provenance.json` (upstream meeting/query ids, revision, license,
  retrieval date, content hashes, the native-ID join deviation).
  `qmsum/selection.json` records the eligibility pool and selection trace.
  Calibration files `calibration/qmsum-01/`, `calibration/qmsum-02/`,
  `calibration/qmsum-03/` (`annotator_a.json`, `annotator_b.json`) record
  human-annotator judgments against these cases.

### QMSum license text (reproduced as MIT requires)

```text
MIT License

Copyright (c) 2021 Yale-LILY

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
