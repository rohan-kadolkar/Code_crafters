import json
"""
PREDICTION & ANALYTICS
Generate predictions and comprehensive student analytics
OPTIMIZED FOR BATCH PROCESSING
-- Robust SHAP integration (uses shap.Explainer and normalizes outputs)
"""
# paste into a util file or at top of predict_analytics.py
from feature_engineering import FeatureEngineer
FEATURE_INFO = {
    "flag_low_attendance": {
        "label": "Low Attendance Flag",
        "category": "Engagement",
        "interpretation": "Student has low attendance or flagged absence pattern.",
        "interventions": [
            "Schedule touchpoint with mentor to discuss attendance barriers.",
            "Offer flexible attendance options or hybrid resources.",
            "Set automated reminders and family notification if needed."
        ]
    },
    "status_attendance_present_days": {
        "label": "Attendance (present days)",
        "category": "Engagement",
        "interpretation": "Number of days the student was present (normalized).",
        "interventions": [
            "Share weekly attendance report with student and parent.",
            "Provide an attendance improvement plan with milestones."
        ]
    },
    "credit_completion_rate": {
        "label": "Credit Completion Rate",
        "category": "Academic Progress",
        "interpretation": "Proportion of credits completed on time.",
        "interventions": [
            "Assign academic advisor to plan course catch-up.",
            "Recommend summer/short courses to complete missing credits."
        ]
    },
    "cumulative_gpa": {
        "label": "Cumulative GPA",
        "category": "Academic Performance",
        "interpretation": "Overall academic performance indicator.",
        "interventions": [
            "Offer targeted tutoring for low-scoring subjects.",
            "Create study plan and weekly progress checks."
        ]
    },
    "fee_pending_count": {
        "label": "Pending Fees",
        "category": "Financial",
        "interpretation": "Count of unpaid fee installments.",
        "interventions": [
            "Connect family with financial aid or payment plans.",
            "Escalate to admin for scholarship review."
        ]
    },
    "total_risk_flags": {
        "label": "Total Risk Flags",
        "category": "Composite",
        "interpretation": "Aggregate count of risk flags across categories.",
        "interventions": [
            "Assign a caseworker to coordinate multi-pronged support."
        ]
    },
    "social_engagement": {
        "label": "Social Engagement",
        "category": "Wellbeing",
        "interpretation": "Measure of participation in social/peer activities.",
        "interventions": [
            "Encourage joining clubs or peer groups.",
            "Assign peer mentor for better integration."
        ]
    }
    # Add any other features you see in shap_explanations...
}


import pandas as pd
import numpy as np
import joblib
import json
import subprocess

# SHAP import (optional)
try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    print("⚠️ SHAP not available. Run: pip install shap")
    SHAP_AVAILABLE = False

# ---------------------------------------------
# SHAP → Root Cause Mapping + Narrative Generator
# ---------------------------------------------

def map_shap_to_root_causes(shap_explanations, top_k=3):
    root_causes = []
    interventions = []
    
    shap_sorted = sorted(shap_explanations,
                         key=lambda x: x.get("importance_pct", 0),
                         reverse=True)[:top_k]
    
    for item in shap_sorted:
        feat = item.get("feature", "")
        info = FEATURE_INFO.get(feat)

        cause = {
            "feature": feat,
            "label": info.get("label") if info else feat,
            "category": info.get("category") if info else "Unknown",
            "contribution": float(item.get("contribution", 0)),
            "importance_pct": float(item.get("importance_pct", 0)),
        }
        root_causes.append(cause)

        if info:
            for action in info.get("interventions", []):
                if action not in interventions:
                    interventions.append(action)

    return root_causes, interventions
import re
def remove_emojis(text):
    return re.sub(
        r"[\U0001F600-\U0001F64F"
        r"\U0001F300-\U0001F5FF"
        r"\U0001F680-\U0001F6FF"
        r"\U0001F1E0-\U0001F1FF"
        r"\U00002700-\U000027BF"
        r"\U0001F900-\U0001F9FF"
        r"\U0001FA70-\U0001FAFF]+",
        "",
        str(text)
    )


def generate_narrative(student_record, top_k=3):
    shap_data = student_record.get("shap_explanations", [])
    causes, actions = map_shap_to_root_causes(shap_data, top_k)

    if not causes:
        return "No clear explanation found.", []

    s = student_record
    statement = (
        f"Student is predicted as {s['dropout_risk']} "
        f"(confidence {s['risk_confidence']}%). "
        "Key influencing factors include: "
        + ", ".join(
            f"{c['label']} ({c['importance_pct']:.1f}%)"
            for c in causes
        ) + "."
    )

    return statement, actions[:5]

class StudentAnalytics:
    def __init__(self, model_dir='models'):
        """Load trained model & preprocessors"""
        self.model = joblib.load(f'{model_dir}/dropout_model.pkl')
        self.scaler = joblib.load(f'{model_dir}/scaler.pkl')
        self.encoders = joblib.load(f'{model_dir}/encoders.pkl')
        self.feature_names = joblib.load(f'{model_dir}/feature_names.pkl')
        self.label_mapping = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}

        self.feature_engineer = FeatureEngineer()
        self.feature_engineer.encoders = self.encoders
        self.feature_engineer.scaler = self.scaler

        # SHAP containers
        self.shap_explainer = None
        self.shap_values_list = None  # will hold list of arrays: [class0, class1, ...]

    def _compute_shap(self, X_scaled):
        """
        Robust SHAP computation using shap.Explainer.
        Converts results to list-of-arrays: shap_values_list[class_index] = (n_samples, n_features)
        """
        if not SHAP_AVAILABLE:
            print("ℹ️ SHAP not available — skipping SHAP computation.")
            self.shap_values_list = None
            return

        try:
            print("🔬 Initializing SHAP explainer (this may take a bit)...")
            explainer = shap.Explainer(self.model)
            shap_out = explainer(X_scaled)  # returns a ShapValues-like object

            # shap_out.values might be:
            # - 2D array (n_samples, n_features) for single-output
            # - 3D array (n_samples, n_features, n_classes) for multiclass
            vals = shap_out.values
            if isinstance(vals, np.ndarray) and vals.ndim == 3:
                # transpose to list per class
                # vals.shape = (n_samples, n_features, n_classes)
                n_classes = vals.shape[2]
                self.shap_values_list = [vals[:, :, c] for c in range(n_classes)]
            elif isinstance(vals, np.ndarray) and vals.ndim == 2:
                # Single output: wrap into list
                self.shap_values_list = [vals]
            else:
                # Fallback: try shap.Explainer(...).shap_values
                print("ℹ️ shap.Explainer produced unusual shape; trying TreeExplainer fallback.")
                te = shap.TreeExplainer(self.model)
                raw = te.shap_values(X_scaled)
                # raw might be list or ndarray
                if isinstance(raw, list):
                    self.shap_values_list = [np.array(r) for r in raw]
                else:
                    if raw.ndim == 3:
                        self.shap_values_list = [raw[:, :, c] for c in range(raw.shape[2])]
                    elif raw.ndim == 2:
                        self.shap_values_list = [raw]
                    else:
                        print("⚠️ Unhandled SHAP output shape:", raw.shape)
                        self.shap_values_list = None

            # DEBUG prints
            if self.shap_values_list is not None:
                shapes = [arr.shape for arr in self.shap_values_list]
                print(f"✅ SHAP computed. per-class shapes: {shapes}")
            else:
                print("⚠️ SHAP produced no usable values.")
        except Exception as e:
            print("⚠️ SHAP computation failed:", e)
            self.shap_values_list = None

    def batch_predict(self, df):
        """
        Predict for multiple students.
        Produces a list of JSON-serializable dicts with SHAP explanations (if available).
        """
        print(f"\n🔮 Processing {len(df)} students in batch mode...")

        student_ids = df['student_id'].values

        print("🔧 Engineering features for all students...")
        df_processed = self.feature_engineer.engineer_features(df.copy())

        # Prepare X with same feature order as training
        X = df_processed[self.feature_names].copy()

        # Safe encoding for categorical features (handle unseen categories)
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            if col in self.encoders:
                encoder = self.encoders[col]
                # collect unique strings in this column
                uniq = set(X[col].astype(str).unique())
                known = set(encoder.classes_)
                unseen = uniq - known
                if unseen:
                    print(f"⚠️ Unseen labels in '{col}': {list(unseen)[:10]} (adding to encoder)")
                    # extend encoder.classes_ (LabelEncoder-like)
                    encoder.classes_ = np.append(encoder.classes_, list(unseen))
                # transform
                X[col] = encoder.transform(X[col].astype(str))

        # Fill NaNs
        X.fillna(0, inplace=True)

        # Scale numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X_scaled = X.copy()
        X_scaled[numeric_cols] = self.scaler.transform(X[numeric_cols])
        # ensure tidy index
        X_scaled.reset_index(drop=True, inplace=True)

        # Compute SHAP for the ENTIRE batch (if available)
        if SHAP_AVAILABLE:
            self._compute_shap(X_scaled)
        else:
            self.shap_values_list = None

        # Generate predictions and probabilities
        print("🎯 Generating predictions...")
        preds = self.model.predict(X_scaled)
        probs = self.model.predict_proba(X_scaled)

        print("📊 Generating individual analytics...")
        results = []
        feature_list = X_scaled.columns.tolist()

        # Iterate and build results; ensure Python native types for JSON
        for idx in range(len(df_processed)):
            student_row = df_processed.iloc[idx]
            pred = int(preds[idx])
            prob = probs[idx]

            dropout_risk = self.label_mapping.get(pred, str(pred))
            risk_confidence = float(round(float(prob[pred]) * 100.0, 6))

            # Basic result structure
            result = {
                "student_id": int(student_ids[idx]),
                "dropout_risk": dropout_risk,
                "risk_confidence": risk_confidence,
                "risk_probabilities": {
                    "Low Risk": float(round(float(prob[0]) * 100.0, 6)),
                    "Medium Risk": float(round(float(prob[1]) * 100.0, 6)),
                    "High Risk": float(round(float(prob[2]) * 100.0, 6))
                }
            }

            # Analytics (strengths, weaknesses, interests, learning_style)
            analytics = self._generate_analytics(student_row)
            # Convert analytics fields to JSON-friendly python types
            result["learning_style"] = str(analytics.get("learning_style"))
            result["strengths"] = [str(x) for x in analytics.get("strengths", [])]
            result["weaknesses"] = [str(x) for x in analytics.get("weaknesses", [])]
            result["interests"] = [str(x) for x in analytics.get("interests", [])]

            # SHAP explanations for predicted class (if available and aligned)
            shap_explanations = []
            if self.shap_values_list is not None:
                try:
                    # Ensure shapes align
                    n_classes = len(self.shap_values_list)
                    # safety: if predicted class index >= n_classes, skip
                    if pred < n_classes:
                        shap_row = self.shap_values_list[pred][idx]  # shape: (n_features,)
                        # ensure length matches feature_list
                        if len(shap_row) == len(feature_list):
                            # Build df for ranking contributions
                            df_feat = pd.DataFrame({
                                "feature": feature_list,
                                "value": X_scaled.iloc[idx].values.tolist(),
                                "contribution": shap_row
                            })
                            df_feat["abs_val"] = np.abs(df_feat["contribution"])
                            df_feat = df_feat.sort_values("abs_val", ascending=False).head(6)

                            for _, r in df_feat.iterrows():
                                # convert numpy types to native python types
                                contribution = float(np.round(float(r["contribution"]), 6))
                                val = r["value"]
                                # if val is numpy scalar
                                if isinstance(val, (np.generic,)):
                                    val = val.item()
                                # if it's array-like then convert first or to list
                                # Here r["value"] is a scalar because we used values.tolist() aligned with features
                                shap_explanations.append({
                                    "feature": str(r["feature"]),
                                    "value": float(val),
                                    "impact": "increases likelihood" if contribution > 0 else "decreases likelihood",
                                    "contribution": contribution,
                                    "importance_pct": float(round(float(np.abs(contribution)) / (float(df_feat["abs_val"].sum()) + 1e-12) * 100.0, 4))
                                })
                        else:
                            # mismatch lengths — debug message
                            print(f"⚠️ SHAP/feature length mismatch for idx {idx}: shap_len={len(shap_row)}, feat_len={len(feature_list)}")
                    else:
                        print(f"⚠️ Predicted class {pred} >= available SHAP classes {n_classes} for idx {idx}")
                except Exception as e:
                    print(f"⚠️ SHAP error idx {idx}: {e}")

            result["shap_explanations"] = shap_explanations

            # Recommendations (keeps previous logic but will be replaced later by smarter engine)
            # 📌 Generate narrative + targeted interventions using SHAP
            narrative, targeted_actions = generate_narrative(result, top_k=3)

            # Save new intelligence outputs
            # Cleanup narrative
            result["explanation_summary"] = remove_emojis(narrative)

            # SHAP root causes (keep same)
            root_causes = result.get("shap_explanations", [])[:3]
            result["root_causes"] = root_causes

            # AI-LLM recommendations (emoji free)
            # AI-based recommendation for Medium/High Risk
            if result["dropout_risk"] != "Low Risk":
                llm_recs = self._llm_recommend(result)
                llm_recs = [remove_emojis(r) for r in llm_recs]  # remove emojis from LLM responses
                result["recommendations"] = llm_recs if llm_recs else [
                    "Stay engaged and ask for help when needed.",
                    "Create a study plan with a mentor to stay on track."
                ]
            else:
                # Static recommendations for Low Risk
                result["recommendations"] = [
                    "Maintain current performance and continue academic engagement.",
                    "Participate in clubs or leadership opportunities.",
                    "Help peers and build confidence through collaboration."
                ]




            results.append(result)

            # optional progress printing
            if (idx + 1) % 200 == 0:
                print(f"   Processed {idx + 1}/{len(df_processed)} students...")

        print(f"✅ Completed predictions for {len(results)} students")
        return results

    def _generate_analytics(self, s):
        """Return analytics dict for a single processed student row (pandas Series)"""
        learning_scores = {
            'Visual': s.get('learning_visual_score', 0),
            'Reading/Writing': s.get('learning_reading_score', 0),
            'Kinesthetic': s.get('learning_kinesthetic_score', 0),
            'Auditory': s.get('learning_auditory_score', 0)
        }
        learning_style = max(learning_scores, key=learning_scores.get)

        strengths = []
        subject_cols = [c for c in s.index if c.startswith('marks_subject_')]
        if subject_cols:
            subj_scores = [(c.replace('marks_subject_', '').replace('_', ' ').title(), s[c]) for c in subject_cols]
            subj_scores = sorted(subj_scores, key=lambda x: x[1], reverse=True)
            strengths += [name for name, sc in subj_scores[:3] if sc > 60]

        if s.get('attendance_percentage', 0) >= 85:
            strengths.append('Excellent Attendance')
        if s.get('assignment_submission_rate', 0) >= 90:
            strengths.append('Assignment Completion')
        if s.get('extra_leadership_roles', 0) > 0:
            strengths.append('Leadership')

        weaknesses = []
        if s.get('attendance_percentage', 100) < 75:
            weaknesses.append('Low Attendance')
        if s.get('assignment_submission_rate', 100) < 70:
            weaknesses.append('Assignment Delays')
        if s.get('fee_pending_count', 0) > 0:
            weaknesses.append('Pending Fees')
        if s.get('extra_participates', 1) == 0:
            weaknesses.append('No Extracurricular Activities')

        interests = []
        activity_cats = ['Technical', 'Sports', 'Cultural', 'Social', 'Academic']
        for cat in activity_cats:
            col = f'extra_category_{cat}'
            if s.get(col, 0) > 0:
                interests.append(cat)
        if s.get('library_visits', 0) > 10:
            interests.append('Reading/Research')
        if s.get('marks_subject_computer_science', 0) > 75:
            interests.append('Computer Science')

        return {
            "learning_style": learning_style,
            "strengths": strengths[:5] if strengths else ['None identified'],
            "weaknesses": weaknesses[:5] if weaknesses else ['None identified'],
            "interests": interests[:5] if interests else ['None identified']
        }

    def _recommend(self, risk, analytics, shap_roots):
        recs = []

        weaknesses = analytics.get("weaknesses", [])
        strengths = analytics.get("strengths", [])

        # 📌 Match SHAP root causes to actions
        for item in shap_roots[:3]:
            feat = item["feature"]

            if "attendance" in feat.lower():
                recs.append("📅 Maintain consistent attendance and classroom engagement.")
            if "gpa" in feat.lower():
                recs.append("📚 Set academic improvement goals with mentor support.")
            if "fee" in feat.lower():
                recs.append("💰 Meet counselor to review fee assistance / scholarships.")
            if "engagement" in feat.lower():
                recs.append("🎯 Participate more in campus clubs / events.")

        # 🎚 Risk-level based supportive actions
        if risk == "High Risk":
            recs += [
                "🚨 Schedule weekly mentor-counselor meetings.",
                "📞 Parent/guardian involvement is required.",
            ]
        elif risk == "Medium Risk":
            recs += [
                "🧑‍🏫 Join subject-support or peer tutoring groups.",
                "⏳ Weekly progress review check-ins."
            ]
        else:  # Low Risk
            recs += [
                "🌟 Keep consistent performance!",
                "🏆 Try leadership roles or competitions.",
                "🤝 Consider helping peers academically."
            ]

        # Strength-based motivators
        if len(strengths) > 0:
            recs.append(f"💪 Utilize strengths: {', '.join(strengths[:2])}.")

        return list(dict.fromkeys(recs))[:6]  # remove duplicates + limit 6

    def _llm_recommend(self, student_result):
        prompt = f"""
            You are an educational counselor AI. Provide a short 2-sentence encouragement message and
            then 5 personalized and actionable recommendations for this student.

            Details:
            - Risk Level: {student_result['dropout_risk']}
            - Risk Confidence: {student_result['risk_confidence']}%
            - Strengths: {student_result['strengths']}
            - Weaknesses: {student_result['weaknesses']}
            - Interests: {student_result['interests']}
            - SHAP Top Risk Factors: {student_result.get('root_causes', [])}

            Ensure recommendations are tailored and non-generic.
            Return output as bullet list only.
            """.strip()

        try:
            result = subprocess.run(
                ["ollama", "run", "llama3"],
                input=prompt.encode("utf-8"),  # 🚀 Proper safe encoding
                capture_output=True
            )
            output = result.stdout.decode("utf-8").strip()
            lines = [remove_emojis(line).strip("•- ") for line in output.split("\n")]
            return [l for l in lines if l][:6]

        except Exception as e:
            print("⚠️ LLM Error:", e)
            return [
                "Stay consistent academically.",
                "Improve attendance and seek help early.",
                "Engage in campus activities for motivation."
            ]


if __name__ == "__main__":
    # Run batch predictions
    df = pd.read_csv("processed_data.csv")
    analytics = StudentAnalytics(model_dir="models")
    print("🔮 Generating predictions for all students...")
    results = analytics.batch_predict(df)

    # Save JSON ensuring everything is serializable
    with open("student_analytics_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Results saved: student_analytics_results.json")
