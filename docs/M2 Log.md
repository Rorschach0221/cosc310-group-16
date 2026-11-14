Menu Item Availability and State Preservation 14th Nov, 2026
Feature Integration

Problem:
The original menu-item model did not support an availability field. This prevented the application from reliably distinguishing between available and unavailable menu items.
During integration, I found another potential issue: updating an unavailable item's information could unintentionally reset its availability to True.

Implementation:
Modified files:
app/schemas/item.py: Added the availability field and non-negative price validation.
app/services/item_service.py: Added availability handling when creating and updating menu items.
app/api/routes/item_router.py: Passed availability information to the service layer and distinguished omitted values from explicit updates.
tests/test_main.py: Added regression coverage for availability preservation and explicit reactivation.

Idea:
The update operation preserves the existing availability state when the request does not explicitly specify a new value. This can prevent an unavailable item from being unintentionally reactivated when other properties are updated.

Testing and Validation:
1 Existing tests remained operational.
2 Added an availability regression test.
3 Verified that availability remains False when a price update omits the field.
4 Verified that explicitly setting availability to True allows reactivation.
Latest pytest result: 18 passed, 1 warning, 0 failed.

AI Assistance:
Used ChatGPT for correcting syntax error.

