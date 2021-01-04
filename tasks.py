from datetime import datetime, timedelta

from invoke import task

# look 2 days ago as the data always exists then
datestr = (datetime.utcnow() - timedelta(days=2)).strftime("%Y%m%d")


@task
def download(ctx, datestr=datestr):
    url = f"https://dumps.wikimedia.org/simplewiki/{datestr}/simplewiki-{datestr}-pages-meta-current.xml.bz2"
    ctx.run(f"curl {url} -o scratch/simplewiki-{datestr}.xml.bz2", echo=True)


@task
def wordcount(ctx, datestr=datestr):
    ctx.run(
        "source env/bin/activate &&"
        f"python script/wordcount.py -m 5 scratch/simplewiki-{datestr}.xml.bz2 scratch/simplewiki-count.csv.gz",
        echo=True,
    )


@task
def update(ctx, datestr=datestr):
    download(ctx, datestr)
    wordcount(ctx, datestr)
    ctx.run("gunzip -c scratch/simplewiki-count.csv.gz | head -n 20", echo=True)
