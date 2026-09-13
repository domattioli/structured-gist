- **Research question: does attention model alignment or more?**
  - **Background**
    - a. NMT progress

      neural machine translation has gained substantial attention recently due to improvements achieving state-of-the-art performance for several languages, built on the general encoder-decoder architecture that learns to encode source sentences into distributed representations and decode them into the target language.
    - b. attentional NMT's advantage

      attentional NMT has become popular for its ability to use the most relevant parts of the source sentence at each translation step, which also makes it superior for translating longer sentences.
  - **Motivating observation**

    an example (Figure FIGREF1) shows attention sometimes "smeared out" over multiple source words whose relevance is not entirely obvious (e.g. "would" and "like"), raising the question of whether this is an attention-mechanism error or desired model behavior.
  - **Gap**
    - a. no prior analysis of attention content

      despite various proposed modifications to attention since its introduction, no study specifically analyzes what kind of phenomena attention captures.
    - b. prior attention-as-alignment work

      some works treat attention as similar to traditional word alignment, and some train the attention model directly using traditional alignments; liu-EtAl:2016:COLING additionally show attention can be seen as a reordering model as well as an alignment model.
  - **Questions asked**
    - is the attention model only capable of modelling alignment?
    - how similar is attention to alignment across different syntactic phenomena?
  - **Headline finding**

    attention models traditional alignment more closely in some cases (nouns show high agreement) while capturing information beyond alignment in others (verbs show attention beyond the translational equivalent).
  - **Contributions**
    - a. detailed comparison

      a detailed comparison of attention in NMT versus word alignment.
    - b. compliance is not always helpful

      different attention mechanisms lead to different degrees of alignment compliance, but global compliance is not always helpful for word prediction.
    - c. patterns by word type

      attention follows different patterns depending on the type of word being generated.
    - d. explanation of divergence

      attention does not always comply with alignment, and the difference is attributable to attention's capability to attend to context words that influence the current word's translation.
- **Related work**
  - a. supervised attention training
    - i. liu-EtAl:2016:COLING

      trains the attention model in a supervised manner using traditional alignments obtained from GIZA++ and fast_align as ground truth fed to the attention network, reporting translation-quality improvements attributed to better source-target alignment.
    - ii. other proponents

      the approach of training attention using traditional alignments has also been proposed elsewhere.
    - iii. chen2016guided

      shows guided attention with traditional alignment helps in e-commerce data containing many out-of-vocabulary product names and placeholders, but yields little benefit in other domains.
    - iv. alkhouli-EtAl:2016:WMT

      separates the alignment and translation models to avoid error propagation between them and gain flexibility in model types/training, using a feed-forward neural network alignment model that learns to model source-side jumps from HMM/IBM alignments obtained via GIZA++.
  - b. attention and linguistic information
    - i. shi-padhi-knight:2016:EMNLP2016

      shows various kinds of syntactic information are learned and encoded in the encoder's output hidden states, using a non-attentional system, and argues attention has no impact on learning syntactic information.
    - ii. belinkov2017neural

      performing the analogous analysis for morphological information, shows attention does have an effect on what the encoder encodes, including that an NMT system with attention learns source-side POS tags more efficiently than one without.
  - c. cross-lingual matching
    - koehn2017six

      carries out a brief cross-language analysis of how much attention and alignment match, by measuring the probability mass attention assigns to alignments from an automatic alignment tool, also reporting differences based on the most-attended words.
  - d. motivating tension

    the mixed results reported by chen2016guided, alkhouli-EtAl:2016:WMT, and liu-EtAl:2016:COLING when optimizing attention with respect to alignments motivate this paper's more thorough analysis.
- **Two attention models studied**
  - a. shared background

    the paper describes two popular attention models used in the analysis; both compute a context vector at each time step, then concatenate it to the decoder hidden state and pass it through a non-linearity before the softmax output layer.
  - b. non-recurrent (global) attention

    equivalent to the "global attention" method; the decoder hidden state is compared to each encoder hidden state (often via dot product), the comparison result is fed to softmax to compute attention weights, and the weighted sum over encoder hidden states gives the context vector.
  - c. input-feeding attention
    - i. origin

      similar to the model first proposed by bahdanau-EtAl:2015:ICLR, generalized and named "input-feeding" by DBLPjournalscorrLuongPM15.
    - ii. mechanism

      at each step the context vector is made aware of the previously computed context by feeding the model's own prior context back into the network, using the resulting hidden state (rather than the context-independent one) to compare against encoder hidden states — where the function is what the stacked LSTM applies to the input, one term is the last generated target word, and another is the previous time step's own output.
- **Comparing attention with alignment**

  it is a commonly held assumption that attention corresponds to word alignments; the paper investigates whether higher attention-alignment consistency leads to better translations.
- **Measuring attention-alignment accuracy**
  - a. soft-alignment conversion
    - i. data source

      manual (hard) alignments come from the RWTH German-English dataset; statistics are given in Table TABREF8.
    - ii. conversion procedure

      hard alignments are converted to soft alignments via a defined equation; unaligned words are first assumed aligned to all source words, then converted the same way, using the set of source words aligned to a given target word and its size.
  - b. attention loss

    after conversion, cross-entropy between attention weights and soft alignment is computed as the attention loss, involving the source sentence, the alignment-link weight between a source and target word, and the attention weight assigned to that source word when generating the target word.
  - c. word prediction loss

    translation quality is measured via word prediction loss: the negative log-probability of the correct target word, using the source sentence, the target word at that time step, the reference-given target history, and the attention-model output.
  - d. correlation metric

    Spearman's rank correlation is used to relate attention loss and word prediction loss, based on the ranks of each, their covariance, and their standard deviations.
  - e. rationale and example

    if word-prediction quality and attention-alignment consistency are closely related, correlation between the two losses should be high; an example (Figure FIGREF13) shows varying consistency levels — for "will" and "come," attention is distributed between the aligned word and others rather than focused on it — and the paper's focus is examining whether such non-alignment-following cases are errors or desirable behavior.
- **Measuring attention concentration**

  as an additional analysis variable, attention concentration is measured via the entropy of the attention distribution, motivated by the observation that word alignments typically involve only one or a few words while attention can be distributed more freely.
- **Empirical analysis setup**
  - a. models used

    the global (non-input-feeding) model from DBLPjournalscorrLuongPM15 and the recurrent input-feeding model; the NMT system is a unidirectional encoder-decoder with 4 recurrent layers.
  - b. hyperparameters

    dimension size 1,000, batch size 80, 20 epochs, vocabulary capped at the 30K most common words per side, learning rate 1, maximum gradient norm 5, dropout rate 0.3 to avoid overfitting.
- **Impact of attention mechanism**
  - a. training data

    both systems trained on WMT15 German-to-English training data (statistics in Table TABREF18).
  - b. BLEU results

    Table TABREF17 reports BLEU scores for both systems across different test sets.
  - c. BPE decision

    BPE is deliberately not used, since the analysis relies on word-level POS tags and dependency roles.
  - d. AER measurement
    - i. definition and purpose

      alignment error rate (AER) is commonly used to measure alignment quality and is reported in Table TABREF20 to show the gap between attentions and human (RWTH) alignments.
    - ii. procedure

      hard alignments are derived from attention by choosing the most-attended source word per target word, following DBLPjournalscorrLuongPM15; GIZA++ is also run (in both directions, symmetrized with the grow-diag-final-and heuristic) to produce automatic alignments for comparison.
  - e. result

    the input-feeding system achieves both a higher BLEU score and attentions closer to the human alignments than the non-recurrent system.
  - f. attention loss comparison

    Table TABREF21 compares input-feeding and non-recurrent attention via attention loss against human alignments; the difference in attention losses is in line with the AER difference.
  - g. AER vs. attention loss distinction

    AER only accounts for the single most-attended word, while attention loss considers the entire attention distribution.
- **Alignment quality impact on translation**
  - a. naive conclusion and its problem

    the BLEU/AER results might suggest closer attention-alignment correspondence yields better translation, but chen2016guided, liu-EtAl:2016:COLING, and alkhouli-EtAl:2016:WMT report mixed results from optimizing NMT toward word prediction and alignment quality jointly, motivating a finer-grained analysis.
  - b. POS-based analysis setup

    the analysis incorporates POS tags of target words, using coarse-grained universal POS tags (Table TABREF25), chosen because they carry simple syntactic characteristics.
  - c. attention loss by POS
    - i. general pattern

      Figure FIGREF22 shows attention loss varies substantially across POS tags; the analysis focuses on NOUN and VERB as the most frequent tags.
    - ii. specific values

      NOUN attention is closest to alignments on average; the average attention loss for VERB is almost twice that of NOUN.
  - d. word prediction loss by POS
    - i. counterintuitive result

      despite higher attention loss for verbs, Figure FIGREF22 shows average word prediction loss for verbs is smaller than for nouns — verbs are translated more accurately on average despite attention being substantially less consistent with alignment.
  - e. correlation by POS

    Spearman's rank correlation between word prediction loss and attention loss, computed per POS tag for the input-feeding model (Figure FIGREF27), formalizes this relationship.
  - f. interpretation
    - i. verbs

      the low correlation for verbs confirms that attending to parts of the source sentence other than the aligned word is necessary for translating verbs, and attention need not follow alignment there.
    - ii. nouns

      the higher correlation for nouns means alignment-consistency of attention is more desirable for that class.
    - iii. explains prior mixed results

      this could explain the mixed results reported for training attention using alignments, especially chen2016guided's large gains in the e-commerce domain (many OOV product names/placeholders) versus weak or no gains in common domains.
- **Attention concentration**
  - a. alignment baseline

    in word alignment, most target words are aligned to a single source word; nouns and verbs are aligned on average to 1.1 and 1.2 source words respectively.
  - b. entropy by POS

    Figure FIGREF28 shows average attention entropy by POS tag; nouns have one of the lowest entropies (concentrated attention), which explains their closeness to alignment.
  - c. entropy-loss correlation for nouns

    the correlation between attention entropy and attention loss is high for nouns (Figure FIGREF28), meaning attention entropy can serve as a proxy for attention-alignment closeness in that case.
  - d. verbs

    verbs show higher attention entropy (more distributed attention, Figure FIGREF28); the low correlation between attention entropy and word prediction loss (Figure FIGREF32) shows concentrated attention is not required for translating verbs, confirming correct verb translation requires attending to different parts of the source sentence.
  - e. pronouns and particles

    pronouns (PRON) and particles (PRT) also show low correlation (Figure FIGREF32) and more distributed attention than nouns (Figure FIGREF28); this is ambiguous between the model "not knowing where to focus" and deliberately attending multiple relevant places — the latter interpretation is supported by their relatively low word prediction losses (Figure FIGREF22).
- **Attention distribution**
  - a. aligned-word attention share

    to understand when attention goes to non-aligned words, the percentage of attention probability mass assigned to aligned words is computed per POS tag (Table TABREF35); for most POS tags, less than half of the attention mass falls on alignment points.
  - b. dependency-role analysis setup

    the remaining attention (beyond alignment points) is examined via dependency roles; the source side of the RWTH data is parsed with the ParZu parser, then the attention mass on non-aligned words is distributed over dependency roles (Table TABREF33).
  - c. results by POS

    for translating to nouns, the most-attended non-aligned roles are adjectives and determiners; for translating to verbs, the most-attended roles are auxiliary verbs, adverbs (including negation), subjects, and objects.
- **Conclusion**
  - a. overall relationship

    attention agrees with traditional alignment to a certain extent, but this differs substantially by attention mechanism and by the type of word being generated.
  - b. noun case

    the concentrated attention pattern and relatively high correlations for nouns show that training attention with explicit alignment labels is useful for generating nouns.
  - c. verb case

    this is not the case for verbs: the large portion of attention on non-aligned words already captures other relevant information, so training attention with alignments there would force the model to forget that useful information.
  - d. explains prior literature

    this explains the mixed results reported when guiding attention to comply with alignments in prior work.
- **Acknowledgments**

  the research was funded in part by the Netherlands Organization for Scientific Research (NWO) under project numbers 639.022.213 and 612.001.218.
