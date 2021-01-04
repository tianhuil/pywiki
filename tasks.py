from datetime import datetime, timedelta

from invoke import task

# wikipedia appears to be dumped on the 1st and 20th of each month
# we will pull the dump from the 1st
now = datetime.utcnow()
first_of_month = now.replace(day=1).strftime("%Y%m%d")


@task
def download(ctx, date=first_of_month):
    url = f"https://dumps.wikimedia.org/simplewiki/{date}/simplewiki-{date}-pages-meta-current.xml.bz2"
    ctx.run(f"curl {url} -o scratch/simplewiki-{date}.xml.bz2", echo=True)


@task
def wordcount(ctx, date=first_of_month):
    ctx.run(
        f"source env/bin/activate &&"
        f"python script/wordcount.py"
        f"  -m 5"
        f"  -s"
        f"  scratch/simplewiki-{date}.xml.bz2"
        f"  scratch/simplewiki-count-{date}.csv.gz",
        echo=True,
    )


@task
def update(ctx, date=first_of_month):
    download(ctx, date)
    wordcount(ctx, date)
    ctx.run("gunzip -c scratch/simplewiki-count.csv.gz | head -n 20", echo=True)
