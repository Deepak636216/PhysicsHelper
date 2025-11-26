# JEE Problem MCP Server - Documentation

## Overview

The JEE Problem MCP Server is a comprehensive Model Context Protocol server that provides access to a rich database of JEE (Joint Entrance Examination) Physics problems. It supports detailed problem metadata including solutions, common mistakes, alternative approaches, NCERT mappings, and pedagogical insights.

## Features

- **19 Problems** across 4 major physics chapters
- **11 MCP Tools** for comprehensive problem exploration
- **Detailed Solutions** with step-by-step explanations
- **Common Mistakes** with correct approaches
- **NCERT Mappings** to textbook chapters
- **Prerequisite Knowledge** tracking
- **Alternative Solution Methods**
- **Key Insights** and learning points

## Problem Coverage

### Chapters
- **Centre of Mass** (4 problems)
- **Laws of Motion** (4 problems)
- **System of Particles and Rotational Motion** (4 problems)
- **Work, Power and Energy** (4 problems)

### Difficulty Levels
- Easy: 5 problems
- Medium: 12 problems
- Hard: 2 problems

### Years Covered
- 2019 (9 problems)
- 2002 (2 problems)
- 1987, 1985, 1984, 1982, 1980 (1 each)

## Available MCP Tools

### 1. `get_problem`
Get problem question and hints without revealing the solution.

**Parameters:**
- `problem_id` (required): Problem identifier (e.g., "COM_Q1_VELOCITY_CM")
- `include_metadata` (optional, default: false): Include concepts, formulas, and NCERT mapping

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM",
  "include_metadata": false
}
```

**Returns:**
- Problem ID, chapter, topic, difficulty
- Year, exam type, marks
- Question text
- Multiple choice options
- Optionally: concepts required, formulas, NCERT mapping

---

### 2. `get_solution`
Get the detailed step-by-step solution for a problem.

**Parameters:**
- `problem_id` (required): Problem identifier

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM"
}
```

**Returns:**
- Correct answer option
- Numerical answer with units
- Official solution with detailed steps
- Answer justification

---

### 3. `get_common_mistakes`
Get common mistakes students make and the correct approaches.

**Parameters:**
- `problem_id` (required): Problem identifier

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM"
}
```

**Returns:**
- List of common mistakes
- Why each mistake is wrong
- Correct approach for each

---

### 4. `get_alternative_approaches`
Get alternative solution methods beyond the official solution.

**Parameters:**
- `problem_id` (required): Problem identifier

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM"
}
```

**Returns:**
- Alternative solution methods
- When each method is useful
- Formulas and explanations

---

### 5. `get_key_insights`
Get key insights and learning points from the problem.

**Parameters:**
- `problem_id` (required): Problem identifier

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM"
}
```

**Returns:**
- Key insights from the problem
- Prerequisite knowledge needed
- Related problems

---

### 6. `search_problems`
Search problems with multiple filters.

**Parameters:**
- `query` (optional): Search keywords in question text
- `chapter` (optional): Filter by chapter name
- `topic` (optional): Filter by specific topic
- `difficulty` (optional): "easy", "medium", or "hard"
- `year` (optional): JEE exam year
- `exam` (optional): Exam type (e.g., "JEE Main")
- `limit` (optional, default: 10): Maximum results to return

**Example Usage:**
```json
{
  "chapter": "Centre of Mass",
  "difficulty": "medium",
  "limit": 5
}
```

**Returns:**
- Applied filters
- Count of results
- Total matches
- List of matching problems

---

### 7. `get_random_problem`
Get a random practice problem with optional filters.

**Parameters:**
- `chapter` (optional): Filter by chapter
- `difficulty` (optional): Filter by difficulty
- `year` (optional): Filter by year

**Example Usage:**
```json
{
  "difficulty": "medium"
}
```

**Returns:**
- Random problem matching the criteria
- Same format as `get_problem`

---

### 8. `list_chapters`
Get all available chapters with statistics.

**Parameters:** None

**Example Usage:**
```json
{}
```

**Returns:**
- Total problem count
- Problems by chapter
- Problems by topic
- Problems by difficulty
- Problems by exam type
- Problems by year

---

### 9. `get_ncert_mapping`
Get NCERT textbook mapping for a problem.

**Parameters:**
- `problem_id` (required): Problem identifier

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM"
}
```

**Returns:**
- NCERT class and chapter
- Chapter number and name
- Relevant sections
- Related NCERT examples

---

### 10. `get_prerequisite_knowledge`
Get prerequisite concepts needed to solve the problem.

**Parameters:**
- `problem_id` (required): Problem identifier

**Example Usage:**
```json
{
  "problem_id": "COM_Q1_VELOCITY_CM"
}
```

**Returns:**
- List of prerequisite concepts
- Required fundamental knowledge
- Concepts explicitly needed in the problem

---

### 11. `get_statistics`
Get overall statistics about the problem bank.

**Parameters:** None

**Example Usage:**
```json
{}
```

**Returns:**
- Total problems
- Distribution by chapter
- Distribution by topic
- Distribution by difficulty
- Distribution by exam type
- Distribution by year

---

## Problem Structure

Each problem in the database contains:

### Basic Information
- `id`: Unique identifier
- `year`: JEE exam year
- `exam`: Exam type (JEE Main/Advanced)
- `date`: Session/date information
- `chapter`: Physics chapter
- `topic`: Specific topic
- `subtopics`: Related subtopics
- `difficulty`: easy/medium/hard
- `marks`: Points for the problem

### Question Details
- `text`: Full question text
- `type`: Question type (objective_single_correct, etc.)
- `options`: Multiple choice options
- `correct_answer`: Correct option ID
- `numerical_answer`: Numerical value
- `units`: Units for the answer

### Learning Content
- `given_data`: All given values with symbols and units
- `concepts_required`: List of concepts needed
- `formulas_used`: Key formulas
- `official_solution`: Step-by-step solution
- `common_mistakes`: Typical errors and corrections
- `alternative_approaches`: Other solution methods
- `key_insights`: Important takeaways
- `prerequisite_knowledge`: Required background

### Metadata
- `ncert_mapping`: Textbook references
- `related_problems`: Similar problems
- `tags`: Search tags
- `has_diagram`: Whether diagram is needed
- `metadata`: Creation and quality info

## Installation & Setup

### Prerequisites
```bash
pip install mcp
```

### Running the Server

#### Standalone Mode
```bash
cd backend/mcp_servers
python problem_server.py
```

#### Testing
```bash
cd backend/mcp_servers
python test_updated_server.py
```

## Integration with AI Tutors

This MCP server can be integrated with AI tutoring systems to:

1. **Progressive Learning**: Start with `get_problem` (no solution), guide through hints
2. **Concept Reinforcement**: Use `get_prerequisite_knowledge` to identify gaps
3. **Mistake Prevention**: Share `get_common_mistakes` proactively
4. **Multiple Methods**: Teach `get_alternative_approaches` for deeper understanding
5. **NCERT Alignment**: Use `get_ncert_mapping` to connect with textbook learning

## Example Workflow

### Socratic Tutoring Workflow
```
1. Student requests a problem
   → Call: get_random_problem(difficulty="medium")

2. Present problem to student
   → Show question and options

3. Student attempts solution
   → If wrong, call: get_common_mistakes(problem_id)
   → Guide student away from known pitfalls

4. Student solves correctly
   → Call: get_solution(problem_id) to show official approach
   → Call: get_alternative_approaches(problem_id) for broader learning

5. Reinforce learning
   → Call: get_key_insights(problem_id)
   → Call: get_prerequisite_knowledge(problem_id) for next steps
```

### Adaptive Practice Session
```
1. Assess student level
   → Call: list_chapters() to see available content

2. Start with easier problems
   → Call: search_problems(chapter="Centre of Mass", difficulty="easy")

3. Track performance
   → Adjust difficulty based on success rate

4. Fill knowledge gaps
   → Use get_prerequisite_knowledge() when student struggles
   → Use get_ncert_mapping() to recommend textbook reading
```

## File Structure

```
backend/
├── data/
│   └── problems/
│       ├── center_of_mass_questions.json
│       ├── laws_of_motion_questions.json
│       ├── rotation_questions.json
│       ├── work_power_energy_questions.json
│       └── sample_problems.json
├── mcp_servers/
│   ├── problem_server.py          # Main MCP server
│   ├── test_updated_server.py     # Test suite
│   ├── test_problem_server.py     # Original tests
│   └── README.md                  # This file
```

## Future Enhancements

- [ ] Add more chapters (Thermodynamics, Electrostatics, etc.)
- [ ] Include problem diagrams and visualizations
- [ ] Add video solution links
- [ ] Support for numerical answer type problems
- [ ] Multi-part question support
- [ ] Student performance tracking
- [ ] Personalized problem recommendations

## Support

For issues or questions about the MCP server:
- Check test file: `test_updated_server.py`
- Review problem structure in JSON files
- Ensure all problem files are in `data/problems/` directory

## Version History

### v2.0.0 (Current)
- Complete restructure for rich JEE problem metadata
- 11 comprehensive MCP tools
- Support for 19 detailed problems across 4 chapters
- Step-by-step solutions with common mistakes
- NCERT mappings and prerequisite knowledge

### v1.0.0
- Basic problem server with 3 sample problems
- 4 simple tools (get_problem, search, random, list_topics)
