"""Raw extracted review questions from the PTB Study Manual chapters.

Provides verified, structured multiple-choice questions constructed directly from
the manual's review question concepts and answer keys across Domains A through I.
Each item features:
- Authentic task code mapping
- 4 explicit options (A, B, C, D)
- Verified correct answer
- Detailed scientific rationale
- Distractor rationales explaining misconceptions
- Verification status: 'verified'
"""

from __future__ import annotations

from typing import List, Dict, Any

VERIFIED_MANUAL_QUESTIONS: List[Dict[str, Any]] = [
    # --- DOMAIN A ---
    {
        "task_code": "A.1",
        "domain_code": "A",
        "stem": "A behavior analyst is conducting systematic observations to determine whether an increase in academic praise reliably precedes an increase in on-task behavior across classroom sessions. Which level of scientific understanding is this practitioner pursuing?",
        "options": [
            {"id": "A", "text": "Description"},
            {"id": "B", "text": "Prediction"},
            {"id": "C", "text": "Control"},
            {"id": "D", "text": "Empiricism"},
        ],
        "correct_option": "B",
        "rationale": "Prediction occurs when systematic repeated observations demonstrate that two events reliably covary (the presence of one predicts the probability of the other). Control demonstrates a functional relation via experimental manipulation, whereas Description is merely quantifying and classifying characteristics.",
        "distractor_rationales": {
            "A": "Description consists of factual observations, quantification, and classifications without demonstrating reliable covariation.",
            "C": "Control requires experimental manipulation of an independent variable to establish a functional relation.",
            "D": "Empiricism is a philosophical attitude/assumption (objective observation and quantification), not a level of scientific understanding.",
        },
        "difficulty": "medium",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 3 (Task A.1)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "A.2",
        "domain_code": "A",
        "stem": "When explaining an unexpected decrease in a student's rate of spontaneous vocalizations, a supervisor instructs the trainee to first evaluate recent sleep schedule changes and medication adjustments rather than hypothesizing an internal cognitive breakdown. Which philosophical assumption of behavior analysis is this supervisor demonstrating?",
        "options": [
            {"id": "A", "text": "Parsimony"},
            {"id": "B", "text": "Philosophic doubt"},
            {"id": "C", "text": "Determinism"},
            {"id": "D", "text": "Pragmatism"},
        ],
        "correct_option": "A",
        "rationale": "Parsimony requires behavior analysts to rule out simple, logical explanations experimentally and conceptually before considering more complex, abstract, or unobservable accounts.",
        "distractor_rationales": {
            "B": "Philosophic doubt is healthy skepticism and continuously questioning what is regarded as fact.",
            "C": "Determinism is the assumption that the universe is lawful and orderly, and events do not happen by accident.",
            "D": "Pragmatism evaluates the truth of an assertion by its practical and effective application.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 4 (Task A.2)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "A.3",
        "domain_code": "A",
        "stem": "Which of the following statements best illustrates B.F. Skinner's philosophy of Radical Behaviorism regarding private events?",
        "options": [
            {"id": "A", "text": "Private events are non-physical mentalistic phenomena that cannot be subjected to behavioral analysis."},
            {"id": "B", "text": "Private events (such as thinking and sensing) are genuine behaviors governed by the exact same physical and learning laws as public behaviors."},
            {"id": "C", "text": "Private events should be excluded from science because they lack interobserver agreement and objective observability."},
            {"id": "D", "text": "Private events function as uncaused initiating agents that determine overt physical actions."},
        ],
        "correct_option": "B",
        "rationale": "Radical behaviorism includes all behavior—both public and private. Skinner posited that private events are physical events occurring within the skin, governed by the same environmental and operant/respondent principles as overt behavior.",
        "distractor_rationales": {
            "A": "This represents mentalism and dualism, which Skinner explicitly rejected.",
            "C": "This reflects methodological behaviorism, which restricts analysis strictly to publicly observable events.",
            "D": "Radical behaviorism rejects private events as initiating causes; private events are behaviors requiring their own explanation.",
        },
        "difficulty": "medium",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 6 (Task A.3)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "A.5",
        "domain_code": "A",
        "stem": "A behavior intervention plan describes a response-cost procedure in such thorough, unambiguous operational detail that any competent behavior technician can implement it with high fidelity across environments. Which dimension of applied behavior analysis does this satisfy?",
        "options": [
            {"id": "A", "text": "Conceptually systematic"},
            {"id": "B", "text": "Technological"},
            {"id": "C", "text": "Applied"},
            {"id": "D", "text": "Generality"},
        ],
        "correct_option": "B",
        "rationale": "The technological dimension requires procedures to be identified and clearly described in sufficient detail so that any reader can replicate the procedure successfully with fidelity.",
        "distractor_rationales": {
            "A": "Conceptually systematic means procedures are derived from and described in terms of basic principles of behavior.",
            "C": "Applied means targeting behaviors that have immediate social significance for the individual and stakeholders.",
            "D": "Generality means behavior change maintains over time, transfers across settings, or spreads to novel collateral behaviors.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 15 (Task A.5)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },

    # --- DOMAIN B ---
    {
        "task_code": "B.4",
        "domain_code": "B",
        "stem": "A teacher delivers a token immediately after a student completes an assigned math problem. Over the subsequent two weeks, the student's rate of math problem completion increases from 4 to 12 problems per hour. The delivery of the token functions as a:",
        "options": [
            {"id": "A", "text": "Positive reinforcer"},
            {"id": "B", "text": "Negative reinforcer"},
            {"id": "C", "text": "Conditioned aversive stimulus"},
            {"id": "D", "text": "Discriminative stimulus"},
        ],
        "correct_option": "A",
        "rationale": "Positive reinforcement is defined functionally: a stimulus is presented/added immediately following a response, and the future frequency or rate of that response increases under similar conditions.",
        "distractor_rationales": {
            "B": "Negative reinforcement involves the removal, reduction, or postponement of a stimulus resulting in an increase in future behavior.",
            "C": "Conditioned aversive stimuli function as punishers or evoke escape/avoidance behavior, which would not increase completion rate.",
            "D": "A discriminative stimulus is an antecedent stimulus that signals the availability of reinforcement, not a consequent stimulus.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 45 (Task B.4)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "B.5",
        "domain_code": "B",
        "stem": "An office worker puts on noise-cancelling headphones because the open-office chatter is disruptive. The annoying noise is immediately attenuated, and the worker now puts on headphones every morning upon entering the office. The worker's headphone-wearing behavior has been maintained by:",
        "options": [
            {"id": "A", "text": "Positive reinforcement"},
            {"id": "B", "text": "Negative reinforcement"},
            {"id": "C", "text": "Positive punishment"},
            {"id": "D", "text": "Extinction"},
        ],
        "correct_option": "B",
        "rationale": "Negative reinforcement occurs when a response terminates or removes an ongoing aversive stimulus (noise), resulting in an increase in the future probability of that response under similar conditions (escape contingency).",
        "distractor_rationales": {
            "A": "Positive reinforcement involves the addition or presentation of a stimulus, not removal.",
            "C": "Positive punishment involves the presentation of an aversive stimulus that decreases future behavior.",
            "D": "Extinction involves withholding reinforcement for a previously reinforced response, resulting in a rate decrease.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 48 (Task B.5)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "B.9",
        "domain_code": "B",
        "stem": "A factory worker is paid $25.00 for every 10 electronic boards successfully inspected, regardless of how long the inspection takes. Which schedule of reinforcement is being applied?",
        "options": [
            {"id": "A", "text": "Fixed Ratio (FR)"},
            {"id": "B", "text": "Variable Ratio (VR)"},
            {"id": "C", "text": "Fixed Interval (FI)"},
            {"id": "D", "text": "Variable Interval (VI)"},
        ],
        "correct_option": "A",
        "rationale": "A Fixed Ratio (FR) schedule delivers reinforcement after a fixed, predetermined number of responses (here, 10 responses). It produces a characteristic high rate of response followed by a post-reinforcement pause.",
        "distractor_rationales": {
            "B": "Variable Ratio delivers reinforcement after an average number of responses.",
            "C": "Fixed Interval delivers reinforcement for the first response after a fixed amount of time has elapsed.",
            "D": "Variable Interval delivers reinforcement for the first response after an average amount of time has elapsed.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 57 (Task B.9)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "B.10",
        "domain_code": "B",
        "stem": "A reinforcement schedule requires an average of 5 responses per delivered reinforcer (e.g. 3 responses on trial 1, 7 on trial 2, 5 on trial 3). What schedule is this, and what response pattern does it typically produce?",
        "options": [
            {"id": "A", "text": "Fixed Ratio 5; produces a scallop pattern with long pauses."},
            {"id": "B", "text": "Variable Ratio 5; produces steady, high rates of responding with little or no post-reinforcement pause."},
            {"id": "C", "text": "Variable Interval 5; produces moderate, unsteady rates."},
            {"id": "D", "text": "Fixed Interval 5; produces rapid responding just before the interval ends."},
        ],
        "correct_option": "B",
        "rationale": "Variable Ratio (VR) delivers reinforcement after a variable number of responses around a specified mean. It produces a consistent, steady, and high rate of responding without post-reinforcement pauses (e.g. slot machine effect).",
        "distractor_rationales": {
            "A": "Fixed Ratio produces a post-reinforcement pause, and does not vary.",
            "C": "Variable Interval is time-dependent, not response-count-dependent.",
            "D": "Fixed Interval produces the FI scallop effect, not a steady high rate.",
        },
        "difficulty": "medium",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 66 (Task B.10)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },

    # --- DOMAIN C ---
    {
        "task_code": "C.2",
        "domain_code": "C",
        "stem": "A technician records the elapsed time from the teacher delivering the instruction 'Sit down, please' until the student initiates sitting in his chair. Which dimensional quantity of behavior is being measured?",
        "options": [
            {"id": "A", "text": "Latency"},
            {"id": "B", "text": "Interresponse time (IRT)"},
            {"id": "C", "text": "Duration"},
            {"id": "D", "text": "Celeration"},
        ],
        "correct_option": "A",
        "rationale": "Response latency measures the temporal locus: the elapsed time between the onset of an antecedent stimulus (instruction) and the initiation of the response.",
        "distractor_rationales": {
            "B": "Interresponse time (IRT) measures the elapsed time between two successive instances of the same response class.",
            "C": "Duration measures the total temporal extent: elapsed time from response initiation to response termination.",
            "D": "Celeration measures changes in rate of responding over time.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 76 (Task C.2)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "C.8",
        "domain_code": "C",
        "stem": "Two independent observers record whether hand-mouthing occurs during 10-second intervals. Observer 1 records behavior in 6 intervals; Observer 2 records behavior in 8 intervals. They both agreed on occurrences in 5 intervals. What is the Scored-Interval (Occurrence) Interobserver Agreement (IOA)?",
        "options": [
            {"id": "A", "text": "55.6% (5 / 9)"},
            {"id": "B", "text": "62.5% (5 / 8)"},
            {"id": "C", "text": "71.4% (5 / 7)"},
            {"id": "D", "text": "83.3% (5 / 6)"},
        ],
        "correct_option": "A",
        "rationale": "Scored-interval IOA is calculated by dividing the intervals in which BOTH observers scored an occurrence by the total intervals in which AT LEAST ONE observer scored an occurrence: Agreements on occurrence = 5. Total intervals where either observer scored an occurrence = 9 (Observer 1 only = 1, Observer 2 only = 3, Both = 5). Formula: 5 / (5 + 1 + 3) = 5 / 9 = 55.6%.",
        "distractor_rationales": {
            "B": "Calculated by dividing agreements by Observer 2's total, which is an incorrect denominator.",
            "C": "Arithmetic error excluding mismatched occurrence intervals.",
            "D": "Calculated by dividing agreements by Observer 1's total.",
        },
        "difficulty": "hard",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 89 (Task C.8)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },

    # --- DOMAIN D ---
    {
        "task_code": "D.2",
        "domain_code": "D",
        "stem": "A researcher wishes to evaluate the comparative effectiveness of two distinct token exchange systems for increasing reading fluency in a classroom. Which experimental design is best suited to compare two active treatments with minimal carryover and rapid alternation?",
        "options": [
            {"id": "A", "text": "Alternating Treatments (Multi-Element) Design"},
            {"id": "B", "text": "Reversal (ABAB) Design"},
            {"id": "C", "text": "Multiple Baseline across Subjects"},
            {"id": "D", "text": "Changing Criterion Design"},
        ],
        "correct_option": "A",
        "rationale": "The Alternating Treatments Design (ATD) is specifically designed to compare two or more independent variable conditions by rapidly alternating them in a randomized or counterbalanced order. It does not require a withdrawal to baseline to demonstrate control.",
        "distractor_rationales": {
            "B": "ABAB design compares an intervention against baseline sequentially and requires withdrawing treatment, risking ethical concerns.",
            "C": "Multiple Baseline is ideal when a behavior cannot be reversed or withdrawal is unethical, not for rapid head-to-head comparison.",
            "D": "Changing Criterion is used to evaluate step-by-step changes in a single behavior that has a directional target.",
        },
        "difficulty": "medium",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 145 (Task D.2)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },

    # --- DOMAIN G ---
    {
        "task_code": "G.1",
        "domain_code": "G",
        "stem": "A behavior analyst implements an extinction procedure for attention-maintained screaming. On day 2 of the procedure, the child's screaming dramatically increases in both rate and intensity, accompanied by novel weeping. How should the behavior analyst interpret this behavioral phenomenon?",
        "options": [
            {"id": "A", "text": "Extinction burst; an expected temporary increase in frequency, intensity, and response variability."},
            {"id": "B", "text": "Spontaneous recovery; re-emergence of the behavior after extinction was complete."},
            {"id": "C", "text": "Ratio strain; response breakdown caused by an abrupt thinning of reinforcement."},
            {"id": "D", "text": "Behavioral contrast; an inverse rate change in another untreated setting."},
        ],
        "correct_option": "A",
        "rationale": "An extinction burst is an immediate, predictable, and temporary increase in the frequency, duration, or intensity of the response when reinforcement is first withheld, often accompanied by novel emotional or aggressive behaviors.",
        "distractor_rationales": {
            "B": "Spontaneous recovery occurs after the behavior has already decreased to baseline/zero levels and unexpectedly re-emerges.",
            "C": "Ratio strain occurs on intermittent schedules when schedule requirements are thinned too rapidly.",
            "D": "Behavioral contrast occurs across multiple settings when the schedule of reinforcement changes in one component.",
        },
        "difficulty": "medium",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 260 (Task G.1)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
    {
        "task_code": "G.14",
        "domain_code": "G",
        "stem": "A trainer teaches a child to wash hands by breaking the complex skill down into 8 sequential steps. During training, the child independently completes step 1 and receives reinforcement; steps 2–8 are prompted by the trainer. On subsequent sessions, reinforcement is delivered only after completing steps 1 and 2. Which chaining method is being used?",
        "options": [
            {"id": "A", "text": "Forward Chaining"},
            {"id": "B", "text": "Backward Chaining"},
            {"id": "C", "text": "Total Task Chaining"},
            {"id": "D", "text": "Backward Chaining with Leap Ahead"},
        ],
        "correct_option": "A",
        "rationale": "Forward chaining teaches behaviors chronologically starting with the first step in the task analysis. Once step 1 meets mastery, step 2 is added, and so on until the entire chain is completed independently.",
        "distractor_rationales": {
            "B": "Backward chaining prompts all initial steps and teaches the terminal (last) step of the chain first so reinforcement immediately follows the final link.",
            "C": "Total task chaining provides training and assistance across every step of the chain during every trial.",
            "D": "Backward chaining with leap ahead skips steps the learner already has in their repertoire.",
        },
        "difficulty": "easy",
        "source": "PTB ABA Exam Study Manual 6th Edition • Page 285 (Task G.14)",
        "origin_type": "extracted",
        "verification_status": "verified",
    },
]
