# 🚀 Recommendation Engine Improvement Plan

## 🔴 CRITICAL FIXES (Do First)

### 1. Fix Interest/Career Matching (BROKEN!)
**Current Issue**: All courses score 0.000 for interest and career alignment
**Root Cause**: TF-IDF/keyword matching algorithms not working properly

**Fixes Needed**:
- Debug `calculate_interest_score()` function
- Improve keyword matching for AI/ML terms
- Add synonyms mapping (AI = artificial intelligence, ML = machine learning)
- Test with actual course descriptions

### 2. Fix Prerequisites Over-Penalization
**Current Issue**: Any course with prereqs gets 0.300 max score, killing advanced courses
**Root Cause**: Too harsh penalty for unmet prerequisites

**Fixes Needed**:
- Reduce prereq penalty: 0.300 → 0.600 minimum
- Add "aspirational" mode for sophomore+ students
- Weight prereqs less for exploration mode
- Consider "soft" vs "hard" prerequisites

## 🟡 MAJOR IMPROVEMENTS (High Impact)

### 3. Course Level Intelligence
**Current Issue**: No awareness that 300-level > 100-level for advanced students
**Solution**: Add course number weighting system

```python
def calculate_course_level_bonus(course_id, academic_level):
    course_num = int(course_id[2:5])  # CS375 -> 375
    
    level_preferences = {
        'freshman': [100, 200],     # Prefer 100-200 level
        'sophomore': [200, 300],    # Prefer 200-300 level  
        'junior': [300, 400],       # Prefer 300-400 level
        'senior': [400, 500]        # Prefer 400+ level
    }
    
    # Bonus for appropriate course level
    if course_num in level_preferences.get(academic_level, []):
        return 0.2  # 20% bonus
    return 0.0
```

### 4. Smarter Weight Distribution
**Current Issue**: Too much weight on structural factors vs interests

**New Weight Structure**:
```python
if is_exploring:
    weights = {
        'interest': 0.15,           # Lower for exploration
        'career': 0.35,             # Higher for career focus
        'level_appropriateness': 0.15,
        'prerequisites': 0.15,      # Reduced penalty
        'popularity': 0.05,
        'course_level_bonus': 0.10, # NEW: Course number intelligence
        'difficulty': 0.05
    }
else:
    weights = {
        'interest': 0.30,           # Higher for focused search
        'career': 0.20,
        'level_appropriateness': 0.15,
        'prerequisites': 0.15,      # Reduced penalty
        'popularity': 0.05,
        'course_level_bonus': 0.10, # NEW: Course number intelligence
        'difficulty': 0.05
    }
```

### 5. Academic Level Contextual Scoring
**Current Issue**: Sophomore gets penalized for wanting junior-level courses

**Solution**: Contextual level scoring
- **Sophomores** should see some junior courses (stretch goals)
- **Juniors** should see senior courses (preparation)
- Add "readiness" vs "appropriateness" distinction

## 🟢 ADVANCED FEATURES (Nice to Have)

### 6. Course Sequence Awareness
**Feature**: Understand course progressions
- If interested in AI, suggest: CS280 → CS301 → CS375 → CS445
- Show prerequisites as "pathway" not "blocker"

### 7. Dynamic Interest Learning
**Feature**: Learn from user interactions
- Track which courses users click on
- Improve matching based on successful recommendations

### 8. Semester Planning Integration
**Feature**: Consider when courses are offered
- Don't recommend Spring-only courses in Fall
- Suggest optimal course sequences by semester

### 9. Professor Ratings Integration
**Feature**: Factor in instructor quality
- Weight popular professors higher
- Show "Dr. Smith teaches this" as bonus

### 10. Peer Recommendations
**Feature**: "Students like you also took..."
- Collaborative filtering
- Similar academic level + interests

## 🎯 IMMEDIATE ACTION PLAN

### Phase 1: Emergency Fixes (Today)
1. **Debug interest matching** - Why everything scores 0.000?
2. **Reduce prerequisite penalties** - 0.300 → 0.600 minimum
3. **Test with CS375 scenario** - Should rank in top 5 for AI/ML sophomore

### Phase 2: Core Improvements (This Week)
1. **Add course level intelligence** - 300-level bonus for sophomores+
2. **Rebalance weights** - More interest/career, less structure
3. **Improve academic level logic** - Sophomores can handle some junior courses

### Phase 3: Advanced Features (Future)
1. **Course sequence awareness** 
2. **Professor integration**
3. **Peer recommendations**

## 🧪 TESTING STRATEGY

### Test Scenarios:
1. **Sophomore + AI/ML** → Should see CS375 in top 5
2. **Senior + AI/ML** → Should see CS445, CS490 (advanced courses)
3. **Freshman + Programming** → Should see CS115, CS116 (appropriate level)
4. **Junior + Web Dev** → Should see CS280, CS388, CS490

### Success Metrics:
- CS375 ranks in top 5 for AI/ML interested sophomores
- Advanced courses appear for advanced students
- Interest matching scores > 0.000 for relevant courses
- Appropriate course level distribution per academic level

## 🔧 IMPLEMENTATION PRIORITY

**Must Fix First**:
1. Interest/Career matching (broken completely)
2. Prerequisite over-penalization
3. Course level intelligence

**High Impact**:
4. Weight rebalancing
5. Academic level contextual scoring

**Future Enhancements**:
6. Course sequences
7. Professor ratings
8. Peer recommendations