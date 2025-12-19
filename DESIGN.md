# API Design Document

## Resources & Requirements

Based on the analysis of the `inventory` app, the primary resource is **Item**.

### **Item Resource**
*   **Purpose:** Represents a tangible inventory object.
*   **Fields:**
    *   `id` (Integer, Primary Key)
    *   `name` (String, required)
    *   `description` (Text, optional)
    *   `status` (Enum: `active`, `archived`, `draft`)
    *   `created_at` (Datetime, read-only)
    *   `updated_at` (Datetime, read-only)
*   **Relationships:**
    *   Currently standalone.
    *   *Future:* `Owner` (User), `Project`, or `Tags`.

### **User Resource (Implicit/Future)**
*   **Purpose:** Authentication and ownership.
*   **Fields:** `id`, `username`, `email`.

---

## REST API Design

The API follows strict RESTful conventions under the `/api/v1/` namespace.

### **Endpoints**

| HTTP Method | Endpoint | Description | Query Params | Success Status |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/v1/items/` | List all items | `?page=1`, `?status=active` | 200 OK |
| **POST** | `/api/v1/items/` | Create a new item | - | 201 Created |
| **GET** | `/api/v1/items/{id}/` | Retrieve an item | - | 200 OK |
| **PATCH** | `/api/v1/items/{id}/` | Update an item (partial) | - | 200 OK |
| **DELETE** | `/api/v1/items/{id}/` | Delete an item | - | 204 No Content |

### **Standard Response Format**

All API responses are wrapped in a standard envelope to ensure consistency for clients.

```json
{
  "data": { ... },     // The resource or list of resources
  "meta": {            // Metadata (pagination, etc.)
    "count": 100,
    "next": "...",
    "previous": "..."
  },
  "errors": [ ... ]    // Array of error objects if applicable
}
```

---

## Proactive Design Decisions

*   **Versioning:**
    *   We use URL path versioning (`/api/v1/`) for explicit control.
    *   Future major breaking changes will introduce `/api/v2/`.
*   **Extensibility:**
    *   The `meta` field in the response is reserved for side-channel data (e.g., rate limits, deprecation warnings) without polluting the `data` object.
*   **Performance:**
    *   **Pagination:** Enabled by default (PageNumberPagination) to prevent massive payloads.
    *   **Field Selection:** (Future) Support `?fields=id,name` to reduce payload size.
*   **Frontend Integration:**
    *   The structure is friendly to Redux/TanStack Query which expects normalized data.
    *   Consistent error handling simplifies frontend form validation logic.

---

## Security & Auth

*   **Strategy:**
    *   **Browser:** Session Authentication (HttpOnly cookies) for the Django-served frontend.
    *   **External/Mobile:** (Future) Token Authentication (JWT or DRF Token) passed via `Authorization: Bearer <token>` header.
*   **Permissions:**
    *   Default policy is `IsAuthenticated`.
    *   Public endpoints (if any) must be explicitly annotated with `AllowAny`.
*   **Rate Limiting:**
    *   (Recommended) Apply DRF `AnonRateThrottle` and `UserRateThrottle`.

---

## Implementation Blueprint (Python/Django)

The implementation leverages **Django REST Framework (DRF)**.

### **Key Components**

1.  **Serializer (`serializers.py`):**
    *   Converts Django models to JSON.
    *   Validates incoming data.

2.  **ViewSet (`api_views.py`):**
    *   Handles the logic for `list`, `create`, `retrieve`, `update`, `destroy`.

3.  **Router (`api_urls.py`):**
    *   Automatically generates URL patterns for the ViewSet.

4.  **Renderer (`renderers.py`):**
    *   Injects the standard `{ data, meta, errors }` envelope.

---

## OpenAPI & Documentation

We use **drf-spectacular** to auto-generate an OpenAPI 3.0 schema.

*   **Schema Endpoint:** `/api/v1/schema/` (YAML/JSON)
*   **Swagger UI:** `/api/v1/docs/`
*   **ReDoc:** `/api/v1/redoc/`

This allows frontend developers to generate TypeScript clients automatically.
