# Exon

Exon is a web API for [Exoline](https://github.com/exosite/exoline), which is a command line application for a web-based product. So it's maybe a bit silly. But it has some features (e.g spec) that are handy to have as an API. You can see Exon running at [https://exon.herokuapp.com](https://exon.herokuapp.com) including a [REPL](https://exon.herokuapp.com/repl).


Here's an example. To call the hosted version of Exoline, do this:

```
$ curl https://exon.herokuapp.com/api -d '{"args": ["lookup", "fac7..."]}'
{
    "exitcode": 0,
    "stderr": "",
    "stdout": "0394b6b901b558584f6f97b26b4c46f8bcba05d5"
}
```

To see what version of Exoline is running, do this:

```
$ curl https://exon.herokuapp.com/api -d '{"args": ["--version"]}'
{
    "exitcode": null,
    "stderr": "",
    "stdout": "Exosite Command Line 0.9.5"
}
```

If you're working at the command line, you might use the excellent [jq](http://stedolan.github.io/jq/) to reconstitute the output:

```
$ curl https://exon.herokuapp.com/api -d '{"args": ["twee", "fac7..."]}' | jq .stdout -r
Attic    cl cik: fac7...
  ├─Battery      dp.s battery: 88 (an hour ago)
  ├─Contact      dp.s contact: closed (an hour ago)
  ├─Event        dp.s event: moved (an hour ago)
  ├─LQI          dp.s lqi: 100 (an hour ago)
  ├─RSSI         dp.s rssi: -41 (an hour ago)
  ├─Temperature  dp.s temperature: 55 (an hour ago)
  ├─X            dp.i threeAxis.x: -995 (an hour ago)
  ├─Y            dp.i threeAxis.y: -32 (an hour ago)
  └─Z            dp.i threeAxis.z: 36 (an hour ago)
```

## Running locally

Create a file called `.env` like this:

```
FLASK_ENV=development
DEBUG=True
```

This gives you debug mode when running locally. Run the server:

```
$ source .env
$ foreman start
```

You can then use Exon at http://localhost:5000.
