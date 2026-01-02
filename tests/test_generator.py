"""Tests for the generator module."""

from fast_llms_txt.generator import generate_llms_txt


class TestGenerateLlmsTxt:
    """Tests for generate_llms_txt function."""

    def test_basic_api_info(self):
        """Test that API title and description are included."""
        schema = {
            "info": {
                "title": "My API",
                "description": "A sample API",
            },
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "# My API" in result
        assert "> A sample API" in result

    def test_multiline_description(self):
        """Test that multiline descriptions are properly formatted."""
        schema = {
            "info": {
                "title": "My API",
                "description": "Line one\nLine two",
            },
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "> Line one" in result
        assert "> Line two" in result

    def test_missing_description(self):
        """Test handling of missing description."""
        schema = {
            "info": {"title": "My API"},
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "# My API" in result
        assert ">" not in result

    def test_endpoint_with_summary(self):
        """Test endpoint formatting with summary."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "### `GET /users` - List users" in result

    def test_endpoint_with_description_fallback(self):
        """Test that description is shown in blockquote when no summary."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "description": "Retrieve all users",
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "### `GET /users`" in result
        assert "> Retrieve all users" in result

    def test_endpoint_grouped_by_tag(self):
        """Test that endpoints are grouped by tag."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "tags": ["Users"],
                        "summary": "List users",
                        "responses": {},
                    }
                },
                "/posts": {
                    "get": {
                        "tags": ["Posts"],
                        "summary": "List posts",
                        "responses": {},
                    }
                },
            },
        }

        result = generate_llms_txt(schema)

        assert "## Users" in result
        assert "## Posts" in result

    def test_default_endpoints_tag(self):
        """Test that endpoints without tags use 'Endpoints' heading."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "## Endpoints" in result

    def test_query_parameter(self):
        """Test query parameter formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"},
                                "description": "Max results",
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`limit` (integer, optional): Max results" in result

    def test_required_parameter(self):
        """Test required parameter formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users/{id}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`id` (string, required) (path)" in result

    def test_request_body(self):
        """Test request body formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name"],
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "User name",
                                            },
                                            "email": {
                                                "type": "string",
                                                "description": "User email",
                                            },
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Body**:" in result
        assert "`name` (string, required): User name" in result
        assert "`email` (string, optional): User email" in result

    def test_response_description(self):
        """Test response description formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {"description": "List of users"},
                            "404": {"description": "Not found"},
                        }
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (200): List of users" in result

    def test_201_response_priority(self):
        """Test that 201 response is used for POST endpoints."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "post": {
                        "responses": {
                            "201": {"description": "User created"},
                            "400": {"description": "Bad request"},
                        }
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (201): User created" in result

    def test_array_type(self):
        """Test array type formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "ids",
                                "in": "query",
                                "schema": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "array[string]" in result

    def test_enum_type(self):
        """Test enum type formatting."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "parameters": [
                            {
                                "name": "status",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "enum": ["active", "inactive"],
                                },
                            }
                        ],
                        "responses": {},
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "enum[active, inactive]" in result

    def test_schema_ref(self):
        """Test $ref resolution in request body."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        },
                        "responses": {},
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "description": "User name"}
                        },
                    }
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`name` (string, required): User name" in result

    def test_multiple_http_methods(self):
        """Test that multiple HTTP methods on same path are handled."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {"summary": "List users", "responses": {}},
                    "post": {"summary": "Create user", "responses": {}},
                }
            },
        }

        result = generate_llms_txt(schema)

        assert "`GET /users`" in result
        assert "`POST /users`" in result

    def test_empty_paths(self):
        """Test handling of empty paths."""
        schema = {
            "info": {"title": "API"},
            "paths": {},
        }

        result = generate_llms_txt(schema)

        assert "# API" in result
        assert "##" not in result

    def test_response_type_from_schema(self):
        """Test that response type is extracted from schema."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"},
                                        }
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {"schemas": {"User": {"type": "object"}}},
        }

        result = generate_llms_txt(schema)

        assert "array[User]" in result

    def test_response_type_with_ref(self):
        """Test response type with $ref."""
        schema = {
            "info": {"title": "API"},
            "paths": {
                "/users/{id}": {
                    "get": {
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        }
                    }
                }
            },
            "components": {"schemas": {"User": {"type": "object"}}},
        }

        result = generate_llms_txt(schema)

        assert "**Returns** (200): User - Success" in result
