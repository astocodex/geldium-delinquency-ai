# Predicting Customer Delinquency at Geldium

A credit-risk analytics project: clean a customer dataset, test whether a model can predict who will miss payments, check it for bias, and turn the result into a recommendation for a Collections team.

> **Context:** I built this during the Tata iQ Data Analytics virtual job simulation on Forage. The company (Geldium), the data and the stakeholders are simulated. It is a learning project, not a real client engagement.

## The short version

I tested six models on 500 customers. **None of them could predict delinquency better than chance**, so my recommendation to the (simulated) Head of Collections was *not* to deploy a model yet, and to run a controlled outreach pilot while the data gets fixed.

I think the honest negative result is the most useful part of this project. It is easy to make a model look good by tuning until the numbers improve. Here I checked whether the result was real (a label-scrambling test), and it was not.

## What I did

| Step | What | Where |
|---|---|---|
| 1. Data audit | Checked missing values and fields that contradict each other | `src/eda.py` |
| 2. Model comparison | Logistic regression, decision tree, random forest, gradient boosting, neural network, with repeated cross-validation | `src/modeling.py` |
| 3. Evaluation | Accuracy, precision, recall, F1, AUC, confusion matrix, and four standard ways to fix a weak model | `src/evaluate.py` |
| 4. Fairness and explainability | Disparate impact, equalized odds, proxy check, per-customer reasons, stability of the reasons | `src/fairness.py` |
| 5. Business recommendation | Segment risk rates, pilot design and sample size | `src/segments.py` |
| 6. Communication | A 2-page business report and a 7-slide executive deck | `docs/` |

## Key findings

**1. The data has real quality problems.** 64 of 500 records (12.8%) have missing Income, Loan_Balance or Credit_Score. Worse, fields contradict each other: 77 customers show zero missed payments in 12 months but have late or missed months in the last six, and 81 customers have an account tenure longer than their adult life (tenure greater than age minus 18). Employment status had six labels for four categories. Missing values were filled with the median inside each cross-validation fold so no test data leaked in.

**2. No model beat chance.**

![Model AUC](outputs/fig_model_auc.png)

| Model | AUC | Delinquency rate in top 20% flagged (overall: 16%) |
|---|---|---|
| Random ranking (baseline) | 0.49 | 15.4% |
| Logistic regression | 0.44 | 12.6% |
| Decision tree (depth 3) | 0.48 | 16.2% |
| Neural network | 0.50 | 17.2% |
| Random forest | 0.40 | 11.0% |
| Gradient boosting | 0.40 | 9.0% |

The real logistic regression scored AUC 0.47 against 0.50 on average for models trained on shuffled labels (p = 0.77), so it cannot be told apart from noise. Oversampling, changing the cutoff, extra features and regularization did not help either (`outputs/improvement_strategies.csv`). Lowering the cutoff to 0.3 raises recall to 86%, but only because 90% of customers get flagged, and flagging everyone would score a higher F1 (0.28) than any cutoff I tried.

**3. Even a model with no real signal can be unfair.**

![Flag rate by location](outputs/fig_flag_rate_by_location.png)

The model flagged Houston customers 34% of the time and New York customers 6.5%, though their real delinquency rates are close (17% and 12%). Retired customers were flagged 7% of the time against 22 to 25% for other employment groups. All four attributes I checked (age band, location, employment, income) fall below the 0.80 disparate-impact guide.

| Attribute | Disparate impact ratio, all fields | Without Age, Location, Employment | Gap still significant? |
|---|---|---|---|
| Location | 0.19 | 0.64 | No (p = 0.50) |
| Employment | 0.28 | 0.55 | No (p = 0.20) |
| Age band | 0.50 | 0.49 | Yes (p = 0.04) |
| Income quartile | 0.44 | 0.42 | Yes (p = 0.003) |

The other fields cannot predict age, location or employment (AUC 0.46 to 0.47, where 0.5 means no ability), so removing those three inputs really does remove the location and employment gaps. The age and income gaps stay, and I flagged them for monitoring.

**4. The explanations were not trustworthy.** The top reason behind the highest-risk customer's score was a missing loan balance, not their behavior. Customers with a missing loan balance were flagged 45% of the time against 18.5% for everyone else. When I refit the model on 200 resampled datasets, only 12% of coefficients kept the same direction in at least 90% of refits.

**5. The recommendation.** The clearest (but not statistically confirmed) pattern was higher debt-to-income and credit utilization: customers above 0.20 debt-to-income were delinquent 17% of the time against 10% at or below it (p = 0.10). Since the model can't say who is high risk, I recommended a 6-week outreach pilot with a random control group. Detecting a drop from 16% to 12% needs about 1,200 customers per group (`outputs/pilot_sample_size.csv`), which is more than this dataset has.

![Delinquency by segment](outputs/fig_delinquency_by_segment.png)

## Limitations

- It is a simulated dataset of 500 customers with only 80 delinquent cases, so every estimate is wide. Several fields look artificially uniform, which suggests the data was generated.
- Fairness numbers come from one set of out-of-sample predictions and one test per attribute. They are screening checks, not a legal audit.
- I had no cost data, so I did not estimate return on investment.
- Thresholds such as 0.65 AUC, 0.80 disparate impact and the 4-point pilot target are my suggestions, not Geldium's.

## How to run

```bash
git clone https://github.com/<your-username>/geldium-delinquency-ai.git
cd geldium-delinquency-ai
pip install -r requirements.txt
# put Delinquency_prediction_dataset.xlsx in data/ (see data/README.md)
python run_all.py
```

Everything takes about 30 seconds. Results are written to `outputs/` (CSV tables and charts). `outputs/run_log.txt` is the console output from my run.

## Project structure

```
src/
  common.py     loading, cleaning and feature setup
  eda.py        data quality checks
  modeling.py   model comparison and label-scrambling test
  evaluate.py   metrics, confusion matrix, improvement strategies
  fairness.py   fairness, proxy and explainability checks
  segments.py   segment rates and pilot sample size
run_all.py      runs everything in order
outputs/        generated tables and charts
docs/           the four deliverables as PDFs
data/           put the dataset here (not included)
```

## Deliverables

1. [EDA summary report](docs/1_EDA_summary_report.pdf)
2. [Model plan](docs/2_model_plan.pdf)
3. [Business report for the Head of Collections](docs/3_business_report.pdf)
4. [AI collections strategy deck](docs/4_ai_collections_strategy_deck.pdf)

## Tools

Python, pandas, NumPy, scikit-learn, SciPy, statsmodels, Matplotlib. I used Claude as an assistant for outlining, code and drafting, and checked every number by running the code in this repository.
