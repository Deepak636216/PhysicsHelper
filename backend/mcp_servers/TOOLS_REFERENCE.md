# MCP Tools Quick Reference

## Tool Categories

### 📚 Problem Discovery
Tools for finding and browsing problems.

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_problems` | Find problems by filters | chapter, topic, difficulty, year, exam |
| `get_random_problem` | Get random practice problem | chapter, difficulty, year |
| `list_chapters` | Browse available content | none |
| `get_statistics` | View problem bank stats | none |

### 📝 Problem Access
Tools for getting problem content (without revealing solutions).

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_problem` | Get question and options | problem_id, include_metadata |

### 💡 Solution & Learning
Tools for accessing solutions and learning content (after attempt).

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_solution` | Step-by-step solution | problem_id |
| `get_common_mistakes` | Common errors to avoid | problem_id |
| `get_alternative_approaches` | Other solution methods | problem_id |
| `get_key_insights` | Learning takeaways | problem_id |

### 🎓 Academic Mapping
Tools for curriculum alignment and prerequisites.

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_ncert_mapping` | Textbook references | problem_id |
| `get_prerequisite_knowledge` | Required concepts | problem_id |

---

## Tool Usage Matrix

### Use Case: Socratic Tutoring Session

| Step | Action | Tool(s) Used | Why |
|------|--------|-------------|-----|
| 1 | Find suitable problem | `search_problems` | Match difficulty to student level |
| 2 | Present question | `get_problem` | Show problem without spoiling solution |
| 3 | Student attempts | - | Let student work independently |
| 4 | Guide if stuck | `get_common_mistakes` | Prevent common errors proactively |
| 5 | Verify answer | `get_solution` | Show correct approach |
| 6 | Deepen understanding | `get_alternative_approaches` | Teach multiple methods |
| 7 | Extract lessons | `get_key_insights` | Reinforce core concepts |
| 8 | Check readiness | `get_prerequisite_knowledge` | Assess gaps |

### Use Case: Adaptive Practice

| Step | Action | Tool(s) Used | Why |
|------|--------|-------------|-----|
| 1 | Assess level | `list_chapters`, `get_statistics` | Understand available content |
| 2 | Start easy | `search_problems(difficulty="easy")` | Build confidence |
| 3 | Random practice | `get_random_problem(difficulty="medium")` | Varied practice |
| 4 | Adjust difficulty | `search_problems` with updated filters | Match performance |
| 5 | Fill gaps | `get_prerequisite_knowledge` | Address weaknesses |

### Use Case: Curriculum Alignment

| Step | Action | Tool(s) Used | Why |
|------|--------|-------------|-----|
| 1 | Match chapter | `search_problems(chapter="Centre of Mass")` | Follow syllabus |
| 2 | Check NCERT mapping | `get_ncert_mapping` | Align with textbook |
| 3 | Verify prerequisites | `get_prerequisite_knowledge` | Ensure readiness |
| 4 | Practice | `get_problem` → solve → `get_solution` | Active learning |

---

## Tool Output Summary

### `get_problem`
```json
{
  "id": "COM_Q1_VELOCITY_CM",
  "chapter": "Centre of Mass",
  "topic": "Velocity of Centre of Mass",
  "difficulty": "easy",
  "year": 2002,
  "question": "...",
  "options": [...]
}
```

### `get_solution`
```json
{
  "id": "COM_Q1_VELOCITY_CM",
  "correct_answer": "c",
  "numerical_answer": 10,
  "units": "m/s",
  "official_solution": {
    "steps": [
      {"step_number": 1, "description": "...", "calculation": "..."},
      ...
    ]
  }
}
```

### `get_common_mistakes`
```json
{
  "id": "COM_Q1_VELOCITY_CM",
  "common_mistakes": [
    {
      "mistake": "Taking average of velocities",
      "consequence": "Gets 7 m/s",
      "correct_approach": "Use mass-weighted average"
    }
  ]
}
```

### `search_problems`
```json
{
  "filters": {"chapter": "Centre of Mass", "difficulty": "medium"},
  "count": 3,
  "total_matches": 3,
  "problems": [
    {"id": "...", "chapter": "...", "question": "..."},
    ...
  ]
}
```

---

## Parameter Reference

### Common Parameters

| Parameter | Type | Values | Example |
|-----------|------|--------|---------|
| `problem_id` | string | Problem identifier | "COM_Q1_VELOCITY_CM" |
| `chapter` | string | Chapter name | "Centre of Mass" |
| `topic` | string | Topic name | "Elastic Collision" |
| `difficulty` | string | easy, medium, hard | "medium" |
| `year` | integer | JEE year | 2019 |
| `exam` | string | Exam type | "JEE Main" |
| `limit` | integer | Max results | 10 |

### Available Values

**Chapters:**
- Centre of Mass
- Laws of Motion
- System of Particles and Rotational Motion
- Work, Power and Energy

**Difficulties:**
- easy (5 problems)
- medium (12 problems)
- hard (2 problems)

**Years:**
- 2019, 2002, 1987, 1985, 1984, 1982, 1980

**Exam Types:**
- JEE Main

---

## Best Practices

### ✅ Do's

1. **Progressive Disclosure**: Start with `get_problem`, only show solution after attempt
2. **Prevent Mistakes**: Check `get_common_mistakes` before showing solution
3. **Multiple Methods**: Always show `get_alternative_approaches` for deeper learning
4. **Check Prerequisites**: Use `get_prerequisite_knowledge` when student struggles
5. **Filter Wisely**: Combine multiple filters in `search_problems` for targeted practice

### ❌ Don'ts

1. **Don't Spoil**: Never call `get_solution` before student attempts
2. **Don't Overwhelm**: Use `limit` parameter to control result count
3. **Don't Ignore Metadata**: `include_metadata=True` provides valuable context
4. **Don't Skip Insights**: Always show `get_key_insights` for learning reinforcement

---

## Tool Dependency Graph

```
search_problems → get_problem
                     ↓
                 [Student attempts]
                     ↓
            get_common_mistakes (optional - if struggling)
                     ↓
                get_solution
                     ↓
        get_alternative_approaches (optional)
                     ↓
             get_key_insights
                     ↓
    ├─ get_prerequisite_knowledge (for next steps)
    └─ get_ncert_mapping (for textbook study)
```

---

## Performance Notes

- **Fast**: `get_problem`, `get_random_problem` (< 10ms)
- **Medium**: `search_problems`, `list_chapters` (< 50ms)
- **Detailed**: `get_solution`, `get_common_mistakes`, etc. (return rich data)

All tools operate on in-memory data loaded at startup (19 problems currently).

---

## Integration Example

```python
# Socratic tutoring workflow
class SocraticTutor:
    def __init__(self, mcp_client):
        self.mcp = mcp_client

    async def tutoring_session(self, student_level="medium"):
        # 1. Find appropriate problem
        result = await self.mcp.call_tool(
            "search_problems",
            {"difficulty": student_level, "limit": 1}
        )
        problem_id = result["problems"][0]["id"]

        # 2. Present problem
        problem = await self.mcp.call_tool(
            "get_problem",
            {"problem_id": problem_id, "include_metadata": True}
        )
        self.present_to_student(problem)

        # 3. Wait for student attempt
        student_answer = await self.get_student_input()

        # 4. Guide through mistakes if wrong
        if not student_answer.is_correct:
            mistakes = await self.mcp.call_tool(
                "get_common_mistakes",
                {"problem_id": problem_id}
            )
            self.guide_student(mistakes)

        # 5. Show solution
        solution = await self.mcp.call_tool(
            "get_solution",
            {"problem_id": problem_id}
        )
        self.explain_solution(solution)

        # 6. Teach alternatives
        alternatives = await self.mcp.call_tool(
            "get_alternative_approaches",
            {"problem_id": problem_id}
        )
        self.teach_alternatives(alternatives)

        # 7. Reinforce learning
        insights = await self.mcp.call_tool(
            "get_key_insights",
            {"problem_id": problem_id}
        )
        self.summarize_lessons(insights)
```

---

## Quick Start Commands

```bash
# Test all tools
python test_updated_server.py

# Run MCP server
python problem_server.py

# Check available problems
# (Use search_problems with no filters via MCP client)
```

---

## Support & Resources

- **Full Documentation**: README.md
- **Restructure Summary**: RESTRUCTURE_SUMMARY.md
- **Test Suite**: test_updated_server.py
- **Problem Files**: ../data/problems/*.json
