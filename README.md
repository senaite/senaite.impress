<div align="center">

  <a href="https://github.com/senaite/senaite.publisher">
    <img src="static/logo.png" alt="SENAITE PUBLISHER" height="64" />
  </a>
  <p>Publication of HTML/PDF Reports in SENAITE</p>

</div>

## Hello World

The easiest way to get started with `senaite.publisher` is to copy a template in
the `templates/reports` folder within this package.


The smallest report example looks like this:

```html
<h1>Hello World!</h1>
```

It renders a heading saying “Hello, world!” on the report.

<img src="static/1_hello_world.png" alt="Hello World" />

The next few sections will gradually introduce you to using `senaite.publisher`.
We will examine single- and multi reports, Zope page templates and the report model.
Once you master them, you can create complex reports for SENAITE.

## Single/Multi Reports

The difference between single- and multi reports is that a single reports
receive a single report object, while multi reports receive a collection of
report objects.

`senaite.publisher` uses the report name to distinguish between a single- and
multi report. A report starting or ending with the workd `Multi`, e.g.
`MultiReport.pt` or `MultiReport.html` will be considered as a multi report and
it will receive all selected objects in a collection.

All other reports, e.g. `Default.pt`, `HelloWorld.pt`, `SingleReport.pt` will be
considered as single reports.

The most basic single report looks like this:

```html
<tal:report define="model python:view.model;">
  <h1 tal:content="model/id">This will be replaced with the ID of the model</h1>
</tal:report>
```

It renders the ID of the model (in this case the Analysis Request `H2O-0001-R01`) on the report.

<img src="static/2_single_report.png" alt="Hello World" />
