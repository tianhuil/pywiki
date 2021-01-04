from datetime import datetime, timedelta

from invoke import task

# wikipedia appears to be dumped on the 1st and 20th of each month
# we will pull the dump from the 1st
now = datetime.utcnow()
datestr = now.replace(day=1).strftime("%Y%m%d")


@task
def download(ctx, datestr=datestr):
    url = f"https://dumps.wikimedia.org/simplewiki/{datestr}/simplewiki-{datestr}-pages-meta-current.xml.bz2"
    ctx.run(f"curl {url} -o scratch/simplewiki-{datestr}.xml.bz2", echo=True)


@task
def wordcount(ctx, datestr=datestr):
    ctx.run(
        f"source env/bin/activate &&"
        f"python script/wordcount.py"
        f"  -m 5"
        f"  -s"
        f"  scratch/simplewiki-{datestr}.xml.bz2"
        f"  scratch/simplewiki-count.csv.gz",
        echo=True,
    )


@task
def update(ctx, datestr=datestr):
    download(ctx, datestr)
    wordcount(ctx, datestr)
    ctx.run("gunzip -c scratch/simplewiki-count.csv.gz | head -n 20", echo=True)
