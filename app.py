import streamlit as st
from matcher import (
    extract_pdf_text,
    compute_similarity,
    get_suggestions,
    apply_suggestions,
    extract_keywords
)
st.title(" Smart Resume Optimizer")
st.set_page_config(layout="wide")
st.write("Upload your resume and paste a job description")


col2,col3=st.columns(2)
with col2:
    uploaded=st.file_uploader("upload your resume")
with col3:
    jd_text=st.text_area("enter your job description")
if st.button("Analyze Resume",use_container_width=True):
    if not uploaded or not jd_text:
        st.warning("please upload your resume and paste a job description")
    else:
        with st.spinner("Analyzing your resume....."):
            resume_text=extract_pdf_text(uploaded)
            score=compute_similarity(resume_text,jd_text)
            suggestions=get_suggestions(resume_text,jd_text)
            resume_keywords=extract_keywords(resume_text)
            jd_keywords=extract_keywords(jd_text)
            matched=resume_keywords & jd_keywords
            missing=jd_keywords-resume_keywords

        st.session_state.resume_text=resume_text
        st.session_state.jd_text=jd_text
        st.session_state.matched=matched
        st.session_state.missing=missing
        st.session_state.suggestions=suggestions
        st.session_state.score=score
if "score" in st.session_state:
    score=st.session_state.score
    suggestions=st.session_state.suggestions
    resume_text=st.session_state.resume_text

    st.divider()

    c2,c3,c4=st.columns(3)
    c2.metric("Match score",f"{score}%")
    c3.metric("Matched keywords",len(st.session_state.matched))
    c4.metric("Missing keywords",len(st.session_state.missing))
    if score<50:
        st.error("Poor match.Please follow the suggestions")
    elif score<75:
        st.warning("Average match.Please follow the suggestions")
    else:
        st.success("Strong match.Please follow the suggestions")
    st.divider()


    st.subheader("Word replacement suggestions")
    if not suggestions:
        st.info("No suggestion found. Your resume looks too good")
    else:
        selected=[]
        for i,s in enumerate(suggestions):
            col_a,col_b,col_c,col_d=st.columns([3,1,3,1])
            with col_a:
                st.write(f"❌ **{s['replace']}**")
            with col_b:
                st.write("→")
            with col_c:
                st.write(f"✅ **{s['with']}**")
            with col_d:
                checked = st.checkbox(
                    "Apply",
                    key=f"chk_{i}",
                    value=True  # default all checked
                )
                if checked:
                    selected.append(s)

        st.divider()

        if st.button("✨ Generate Improved Resume Text", use_container_width=True):
            if selected:
                improved = apply_suggestions(resume_text, selected)

                st.subheader("📄 Improved Resume Text")
                st.text_area(
                    "Copy this improved text into your resume:",
                    value=improved,
                    height=400
                )

                # recalculate new score
                new_score = compute_similarity(improved, st.session_state.get("jd_text", ""))
                if new_score > score:
                    st.success(f"🎉 New Match Score: {new_score}% (was {score}%)")
            else:
                st.warning("Please select at least one suggestion to apply.")




