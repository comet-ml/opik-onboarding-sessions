# Opik Optimization Studio Demo — CRM Optimizer

This demo shows how to use [Opik Optimization Studio](https://www.comet.com/docs/opik/agent_optimization/optimization_studio) to iteratively improve a **CRM advisor prompt** that helps sales and revenue teams solve real-world CRM challenges.

---
## 1 — Upload the dataset

Upload the dataset from the Opik UI. 

Name: **"CRM Optimizer - Q&A"**  

Each item has a `question` and an `answer` field.

---

## 3 — Configure Optimization Studio

Open **Opik UI → Optimization Studio → New Optimization** and fill in the form:

### Run name

```
CRM Advisor Prompt v1
```

### Model

Select **gpt-4o** (or whichever model you prefer).

### Prompt messages

**System message (starting prompt — intentionally weak):**

```
You are a CRM assistant. You help sales teams with their CRM-related questions. When someone asks you a question, think about what a CRM consultant would recommend and provide your best advice. Try to be helpful and cover the main points of the topic. If relevant, mention tools or features that might exist in a CRM platform.

{{question}}
```

This prompt sounds reasonable but is weak in ways the G-Eval criteria will catch: it has no specific persona or expertise level, doesn't require structured steps or metrics, uses hedging language ("try to", "if relevant", "might exist"), and gives no formatting guidance. This gives the optimizer clear room to improve.

> The `{{question}}` placeholder will be replaced with each dataset item's `question` field.

**Stronger alternative (for a second run or comparison):**

```
You are a senior CRM strategy consultant with 15 years of experience helping B2B SaaS companies optimize their sales processes, customer retention, and revenue operations. When given a CRM-related question, provide a detailed, actionable response that includes specific steps, recommended metrics, and practical implementation guidance. Structure your answer so a sales ops manager could execute it within their CRM platform.

Answer the following question:
{{question}}
```

### Algorithm

Select **Hierarchical Reflective** 

### Dataset

Select **CRM Optimizer - Q&A** (the dataset you just uploaded).

### Metric — G-Eval

Select **Custom (G-Eval)** and configure it as follows:

**Task introduction:**

```
You are evaluating a CRM strategy advisor. The advisor receives a question about a CRM challenge (pipeline management, lead scoring, churn reduction, upselling, forecasting, etc.) and must provide a detailed, actionable response.

The reference answer is:
{{answer}}
```

> The `{{answer}}` placeholder will be replaced with each dataset item's `answer` field, giving the evaluator the ground truth to compare against.

**Evaluation criteria:**

```
1. Actionability (0-10): Does the response provide concrete, specific steps that a sales ops manager could execute immediately? 0: vague platitudes like "improve your process" with no concrete actions. 5: some actionable suggestions but missing timelines, ownership, or measurable outcomes. 10: a numbered playbook with clear steps, timelines, ownership, and measurable outcomes.

2. CRM Depth (0-10): Does the response demonstrate expertise with CRM-specific concepts such as deal stages, lead scoring fields, automation workflows, health scores, dashboards, or custom objects? 0: generic business advice with no CRM specificity. 5: mentions CRM concepts but stays surface-level. 10: deep, practical CRM guidance referencing specific features, fields, and configurations.

3. Alignment with Reference (0-10): Does the response cover the same key recommendations and strategic direction as the reference answer? 0: contradicts or completely misses the reference answer's core advice. 5: covers some key points but omits important recommendations. 10: consistent with the reference in strategy direction and covers all major recommendations, even if wording differs.
```

---

## 4 — Run the optimization

Click **Optimize prompt** and watch the progress chart. The number of trials is managed automatically by the algorithm. Optimization Studio will:

1. Evaluate your initial prompt against the dataset.
2. Generate prompt variations using the selected algorithm.
3. Score each variation with G-Eval.
4. Surface the best-performing prompt.

---

## 5 — Analyze results

- **Progress chart**: Shows the best score over time — look for a clear upward trend.
- **Trials tab**: Compare the exact prompt text and score for each trial. Click a trial to see per-item scores and identify which questions the prompt struggles with.
- **Best prompt**: Copy the winning prompt and use it in production or as the starting point for a second optimization round.

