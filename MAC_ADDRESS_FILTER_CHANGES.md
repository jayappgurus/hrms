# MAC Address Page - Status Filter Implementation

## Changes Made

### 1. View Updates (`employees/views_system_management.py`)

Added status filtering logic to the `show_mac_address` view:

```python
# Get filter parameter from URL query string
status_filter = request.GET.get('status', 'all')

# Apply filter based on is_active field
if status_filter == 'assigned':
    mac_systems = mac_systems.filter(is_active=True)
elif status_filter == 'pending':
    mac_systems = mac_systems.filter(is_active=False)
```

### 2. Template Updates (`templates/system/show_mac_address.html`)

#### Added Filter Section
- Dropdown to select status: All Systems / Assigned / Pending
- Auto-submits on change
- Clear filter button when filter is active

#### Added Status Column
- New column in the table showing assignment status
- Green badge with checkmark for "Assigned" systems
- Yellow badge with clock for "Pending" systems

## Features

### Filter Options
1. **All Systems** - Shows all MAC addresses (default)
2. **Assigned** - Shows only systems with `is_active=True`
3. **Pending/Non-allocated** - Shows only systems with `is_active=False`

### Status Badges
- ✅ **Assigned** - Green badge (`bg-success`)
- ⏰ **Pending** - Yellow badge (`bg-warning`)

## How It Works

1. User selects a status from the dropdown
2. Form auto-submits with `?status=assigned` or `?status=pending` query parameter
3. View filters the queryset based on the parameter
4. Template displays filtered results with status badges
5. "Clear Filter" button appears when a filter is active

## URL Examples

```
# Show all systems
/employees/show-mac-address/

# Show only assigned systems
/employees/show-mac-address/?status=assigned

# Show only pending systems
/employees/show-mac-address/?status=pending
```

## Testing

To test the implementation:

1. Navigate to MAC Address Assignments page
2. Use the "Filter by Status" dropdown
3. Verify the table updates to show only filtered results
4. Check that status badges display correctly
5. Test the "Clear Filter" button

## Database Field Used

- `SystemDetail.is_active` (BooleanField)
  - `True` = Assigned/Allocated
  - `False` = Pending/Non-allocated
