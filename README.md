# Multi Layer Filter Toolbar (QGIS Plugin)


Quickly filter multiple vector layers directly from the toolbar.

![](docs/images/toolbar.png)

This extension allows you to select multiple layers in the layer tree and apply a common expression filter to all of them in a single click.
It includes a filter history and direct access to the QGIS expression builder.

## Features

- Select multiple vector layers from the current QGIS project
- Apply a common expression filter to all selected layers
- Build expressions using the QGIS expression builder
- Reuse previous expressions from the history list
- Clear active filters in one click

## Usage

1. Click the layer selection button
2. Select the vector layers you want to filter
3. Enter a valid QGIS expression (with or without QGIS expression builder), example:
```sql
"status" = 'in service'
```
4. Press Enter or click the filter button
5. Click the clear button to remove the active filters

# Changelog
* 1.0.1 Added translations for French, German, Spanish, Italian, and Portuguese
* 1.0.0 Initial Release

# Planned Improvements
* Save selected layers in project file

## License

See the repository’s [LICENSE](./LICENSE.md) file.