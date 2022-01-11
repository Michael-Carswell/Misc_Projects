from invoke import task

@task(name = "convert")
def openwebpage(c, url = None):
    if url:
        c.run(f"start {url}")
    else: 
        print("I need a file name to run!")

@task(name = "plot")
def firststep(c):
    print("going to perform the first step!")

@task(name = "thirdstep")
def thirdstep(c):
    print("going to perform the third step!")

@task(name = "secondstep", pre = [firststep], post = [thirdstep])
def secondstep(c):
    print("this is the main thing happening")