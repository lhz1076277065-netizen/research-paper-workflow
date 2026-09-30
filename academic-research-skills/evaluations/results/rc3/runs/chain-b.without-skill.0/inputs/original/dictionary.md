# Synthetic data dictionary, version 1
event_id identifies a single measurement event. An exact duplicate of an event
is an archive copy, not a new observation; conflicting values would need review.
unit_id is the independent paired unit. Technical repetitions within unit/method
are equally precise here; estimate that unit/method by its mean after conversion.
1 score = 1000 subscore. All raw values use measurement_unit explicitly.
Join unit metadata by unit_id AND observed_at within inclusive valid_from/to.
Metadata contains history: there is exactly one active record per observation.
The eight units are independent conditional on stratum for this fixture's
within-stratum resampling model. Generalization to a real population is unknown.
Target weights (0.8,0.2) were stipulated before measurements. There are four
observed units in each stratum. No real data or real-world validation is present.
