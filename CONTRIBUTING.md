# Contributing to Rangmanch Review API

Thank you for helping improve this project. It is small on purpose, so the most valuable contributions keep it **clean, simple and well documented**. This guide explains how to set up, what we expect from code, and how to document the API.

## Contents

1. [Getting set up](#getting-set-up)
2. [Ways to contribute](#ways-to-contribute)
3. [Clean and simple code](#clean-and-simple-code)
4. [API design structure](#api-design-structure)
5. [Documentation: follow the OpenAPI standard](#documentation-follow-the-openapi-standard)
6. [Meaningful comments](#meaningful-comments)
7. [Working on the custom docs UI](#working-on-the-custom-docs-ui)
8. [Commits, branches and pull requests](#commits-branches-and-pull-requests)

## Getting set up

This project uses [uv](https://docs.astral.sh/uv/). You do not need to create or activate a virtual environment yourself.

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/Zain-Ahma12/Rangmanch-Review-api.git
cd Rangmanch-Review-api

# 2. Create virtual environment and activate it
uv venv .venv

.venv\Scripts\activate  # (for windows)

# 2. Install dependencies (runtime + dev tools such as Ruff)
uv pip install requirements.txt

# 3. Run the API with auto-reload
python main.py
```

Open `http://127.0.0.1:8000/docs`. If you can create, list, update and delete a review there, your setup works.

Before you push, run the formatter and linter:

```bash
uv run ruff format .
uv run ruff check .
```

## Ways to contribute

- **Report a bug.** Open an issue with the steps to reproduce, what you expected, what happened, and your Python version and operating system.
- **Suggest a feature.** Open an issue first and describe the problem you want to solve. Small, focused changes are easier to review and merge than large ones.
- **Improve the docs.** Fixing a typo, clarifying an example or adding a missing description is always welcome.
- **Fix an issue or add a feature.** Comment on the issue so nobody duplicates the work, then follow the rules below.

## Clean and simple code

The goal is code that a new teammate can read once and understand. When two solutions work, choose the simpler one.

- **Follow PEP 8**, and let Ruff do the formatting. Line length is 100.
- **Use type hints** on every function signature, including the return type where it is not obvious.
- **Keep functions short and focused.** If a function does two things, split it. A route handler should read like a short story: get the data, check it, return it.
- **Use clear names.** `get_average_rating` beats `calc`. Write `query`, not `querry`. Avoid single-letter names except for short loops.
- **Return early.** Handle the error case first so the main path is not nested.
- **No clever tricks.** Prefer an obvious `for` loop over a dense one-liner when it is easier to read.
- **No dead code.** Delete unused imports, variables and commented-out blocks. Git remembers them.
- **Keep one responsibility per module.** Routes stay in `routes/`, data models in `model.py`, database setup in `database.py`, and error classes and handlers in `exceptions/`.
- **Do not add a dependency** for something the standard library or the current stack already does. If you must add one, explain why in your pull request.

A small example of the difference:

```python
# Hard to follow: nested, and the happy path is buried
def get_review_for_id(id: int, session: Session):
    review = session.get(Review, id)
    if review:
        return review
    else:
        raise InvalidReviewIdError(id)

# Clear: guard first, then return
def get_review_for_id(id: int, session: Session) -> Review:
    review = session.get(Review, id)
    if review is None:
        raise InvalidReviewIdError(id)
    return review
```

## API design structure

New endpoints must fit the existing structure so the API stays predictable.

### Project layers

| Layer | File | Responsibility |
| --- | --- | --- |
| App wiring | `main.py` | Create the app, register the router and exception handlers, set up the lifespan |
| Routes | `routes/reviews.py` | HTTP concerns only: parse input, call the database, return a response |
| Models and schemas | `model.py` | The database table and the request / response schemas |
| Database | `database.py` | Engine, table creation, and the `get_session` dependency |
| Errors | `exceptions/` | Domain exceptions and the handlers that turn them into JSON |

A new resource gets its own router file (for example `routes/plays.py`) with its own `prefix` and `tags`, which is then included in `main.py`.

### URLs and methods

- Use **plural nouns** for collections and no verbs in paths: `/reviews`, not `/getReviews`.
- Use **lowercase** paths. Use a path parameter to identify one item: `/reviews/{id}`.
- Put **filters and pagination in query parameters**, not in the path: `?play_name=Hamlet&skip=0&limit=10`.
- Declare **fixed paths before parameterised ones**. `/reviews/average/{play_name}` must come before `/reviews/{id}`, or the second route captures the first.

| Action | Method | Path | Success status |
| --- | --- | --- | --- |
| Create | `POST` | `/reviews/` | `201 Created` |
| List | `GET` | `/reviews/` | `200 OK` |
| Read one | `GET` | `/reviews/{id}` | `200 OK` |
| Partial update | `PATCH` | `/reviews/{id}` | `200 OK` |
| Delete | `DELETE` | `/reviews/{id}` | `204 No Content` (empty body) |

### Schemas

Keep a separate schema for each purpose, as the `Review` family does:

- `Review`: the database table (`table=True`).
- `ReviewCreate`: what a client may send when creating. It never includes `id` or `created_at`.
- `ReviewRead`: what the API returns. Use it as the `response_model`.
- `ReviewUpdate`: every field optional, with a `None` default, so `PATCH` accepts partial input.

Never return a table model directly. Always set `response_model`.

### Errors

- Raise a **domain exception** (for example `InvalidReviewIdError`) from the route. Do not build `JSONResponse` objects inside routes.
- Add the exception class and its handler in `exceptions/`, then register the handler in `main.py`.
- Error bodies keep the same shape: a stable snake_case `error` code, a human-readable `message`, and the value that caused the problem.

```json
{ "error": "review_id_not_found", "message": "No data for review id: 42", "id": 42 }
```

### Database access

- Get a session with `Depends(get_session)`. Never create a session inside a route.
- Always cap list endpoints with `limit` and give them a stable `order_by`, so pagination is repeatable.
- Store timestamps in UTC: `datetime.now(timezone.utc)`.

## Documentation: follow the OpenAPI standard

FastAPI generates an [OpenAPI](https://spec.openapis.org/oas/latest.html) document from your code, and the `/docs` page is built from it. The documentation is therefore part of the code. An endpoint without documentation is not finished.

### Every endpoint needs

- `summary`: a short, imperative title, such as "Get a review".
- A **docstring** that explains behaviour in plain language. FastAPI uses it as the endpoint `description`, and Markdown works.
- `tags`: set once on the router, so endpoints are grouped.
- `response_model` and `status_code`.
- `responses` for every documented error status, such as `404`.
- `Query(...)` and `Path(...)` parameters with a `description`.

```python
@router.get(
    "/{id}",
    response_model=ReviewRead,
    status_code=status.HTTP_200_OK,
    summary="Get a review",
    responses={404: {"description": "No review exists with this id."}},
)
def get_review_for_id(
    id: int = Path(description="Id of the review to fetch"),
    session: Session = Depends(get_session),
) -> Review:
    """Return a single review by its id."""
    review = session.get(Review, id)
    if review is None:
        raise InvalidReviewIdError(id)
    return review
```

### Every schema needs

- A `description` on each field, plus its constraints (`ge`, `le`, `min_length`) so they appear in the schema.
- An example, so the "Try it out" body is realistic instead of `"string"`.

```python
class ReviewCreate(SQLModel):
    """Data a client sends to create a review."""

    play_name: str = Field(description="Title of the play being reviewed")
    reviewer_name: str = Field(description="Name shown next to the review")
    rating: int = Field(ge=0, le=5, description="Star rating from 0 (worst) to 5 (best)")
    comment: str = Field(description="Free-text feedback")

    model_config = {
        "json_schema_extra": {
            "example": {
                "play_name": "Hamlet",
                "reviewer_name": "Asha",
                "rating": 5,
                "comment": "A powerful evening.",
            }
        }
    }
```

### Rules of thumb

- Operation ids must be unique. FastAPI generates them from the function name and path, so give every route function a unique, descriptive name. Two functions with the same name, such as two called `update_review_for_id`, are a bug.
- Describe what the endpoint does and returns, not how it is implemented.
- Document status codes honestly. If an endpoint can return `404` or `422`, say so.
- After changing an endpoint, open `/docs` and `/openapi.json` and check that the summary, parameters, example and responses look right. You can also lint the schema with a tool such as [Spectral](https://github.com/stoplightio/spectral).
- Update the endpoint table in `README.md` when you add, remove or rename an endpoint, and update `docs/architecture.drawio` and `docs/architecture.svg` to match.

## Meaningful comments

Code shows **what** happens. Comments should explain **why**, and anything a reader could not guess.

- Write a **docstring** for every public function, class and module. This project uses the Google style (`Args:`, `Returns:`, `Raises:`), as in `exceptions/`.
- Comment on **decisions, trade-offs and gotchas**: why an order matters, why a limit exists, why a workaround is needed.
- Keep comments **short and up to date**. A wrong comment is worse than none. If you change the code, change the comment.
- **Do not restate the code.** If the comment repeats the line below it, delete it.
- **Do not leave commented-out code.** Remove it.
- Write `TODO(your-name): ...` with a reason, and link an issue when there is one.

```python
# Bad: repeats the code
# Add the review to the session
session.add(review)

# Bad: explains nothing a reader cannot see
# Check if review exists
if review is None:

# Good: explains why
# Declared before "/{id}" so FastAPI does not treat "average" as a review id.
@router.get("/average/{play_name}")

# Good: explains a limit
# Cap at 50 so a single request cannot read the whole table.
limit: int = Query(10, ge=1, le=50)
```

## Working on the custom docs UI

The themed `/docs` page lives in `docs_ui.py`.

- Colours are CSS variables at the top of the stylesheet. Change a token there, not a hard-coded colour further down.
- Test **both** light and dark themes, and a narrow screen (under 860 px wide).
- Keep text contrast at WCAG AA (4.5:1 for normal text, 3:1 for large text and control borders).
- Respect `prefers-reduced-motion`. Motion should explain a change, not decorate.
- Swagger UI is pinned to one version because the CSS targets its markup. If you bump the version, check every operation state: collapsed, expanded, "Try it out", a response, and the schemas section.

## Commits, branches and pull requests

- Create a branch from `main` with a descriptive name, such as `feat/review-sorting` or `fix/delete-status-code`.
- Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org/) style: `feat: add sorting to list reviews`, `fix: return 204 with an empty body on delete`, `docs: describe the average endpoint`.
- Keep each pull request to one logical change.

### Pull request checklist

- [ ] The app starts with `python main.py` and the change works in `/docs`
- [ ] New or changed endpoints follow the [API design structure](#api-design-structure)
- [ ] Every endpoint and schema is documented as described in the [OpenAPI section](#documentation-follow-the-openapi-standard)
- [ ] Comments explain why, and no commented-out code is left behind
- [ ] `README.md` and the architecture diagram are updated if endpoints changed

## Code of conduct

Be kind, be patient and assume good intent. Give feedback on the code, not the person. Harassment or personal attacks are not tolerated.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
