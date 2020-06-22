
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from mpl_toolkits.mplot3d import Axes3D
import sys
from scipy.stats import norm
import pylab
import re

Boards = [7,8]
Nodes  = [0]

def extractFileData(fname):
    grps = re.match(r'(\d+)_(\d+)\.dat',fname)

    return int(grps[1]), int(grps[2])

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} data_file.dat")
    sys.exit()

inFiles = sys.argv[1:]
print(f"Input files: {inFiles}")
summary = {}

# Determine which channels and thresholds are begin scanned for summary
sumTholds   = []
sumChannels = []

for fname in inFiles:
    channel, thold = extractFileData(fname)

    if channel not in sumChannels:
        sumChannels.append(channel)

    if thold not in sumTholds:
        sumTholds.append(thold)

sumTholds.sort()
sumChannels.sort()

for node in Nodes:
    if node not in summary:
        summary[node] = {}

    for board in Boards:
        if board not in summary[node]:
            summary[node][board] = {}

        for rena in range(2):
            if rena not in summary[node][board]:
                summary[node][board][rena] = {}

            for channel in sumChannels:

                if channel not in summary[node][board][rena]:
                    summary[node][board][rena][channel] = {'pol': 0, 'data': {}}

                for thold in sumTholds:
                    if thold not in summary[node][board][rena][channel]['data']:
                        summary[node][board][rena][channel]['data'][thold] = {'hits': 0, 'mean' : 0.0, 'sigma' : 0.0}


for inFile in inFiles:
    outFile = inFile + ".pdf"

    fileChan, thold = extractFileData(inFile)

    print(f"Processing {inFile} with channel {fileChan}, threshold {thold}")

    plots = {}

    # Init Data
    for node in Nodes:
        if node not in plots:
            plots[node] = {}

        for board in Boards:
            if board not in plots[node]:
                plots[node][board] = {}

            for rena in range(2):
                if rena not in plots[node][board]:
                    plots[node][board][rena] = {}

                for channel in range(36):
                    if channel not in plots[node][board][rena]:
                        plots[node][board][rena][channel] = {'pha' : [], 'pol': 0, 'uVal' : [], 'vVal' : []}

    print("Reading data......")
    ct = time.time()
    count = 0

    with open(inFile) as f:
        for line in f:
            data = line.rstrip().split(' ')

            node   = int(data[0])
            board  = int(data[1])
            rena   = int(data[2])
            chan   = int(data[3])
            pol    = int(data[4])
            pha    = int(data[5])
            uVal   = int(data[6])
            vVal   = int(data[7])
            tstamp = int(data[8])

            plots[node][board][rena][chan]['pol']  = pol
            plots[node][board][rena][chan]['vVal'].append(vVal)
            plots[node][board][rena][chan]['uVal'].append(uVal)
            if pha != 0:
                plots[node][board][rena][chan]['pha'].append(pha)

            if int(ct) != int(time.time()):
                print(f"Read {count} entries")
                ct = time.time()

            count += 1

    print("Done reading data")
    print("Generating plots....")

    pdf = matplotlib.backends.backend_pdf.PdfPages(outFile)
    figs = plt.figure()
    fig = None
    idx = 0

    for node in Nodes:
        for board in Boards:
            for rena in range(2):
                for channel in range(36):

                    # Only plot channels with data
                    if len(plots[node][board][rena][channel]['pha']) != 0:
                        pol = plots[node][board][rena][channel]['pol']

                        pha_path = plots[node][board][rena][channel]['pha']
                        mean_sigma = norm.fit(pha_path)

                        if channel in summary[node][board][rena]:
                            summary[node][board][rena][channel]['pol'] = pol

                            if thold in summary[node][board][rena][channel]['data']:

                                summary[node][board][rena][channel]['data'][thold]['hits'] = len(plots[node][board][rena][channel]['pha'])
                                summary[node][board][rena][channel]['data'][thold]['mean'] = mean_sigma[0]
                                summary[node][board][rena][channel]['data'][thold]['sigma'] = mean_sigma[1]

                        # Start of a new page
                        if (idx % 4) == 0:
                            fig = plt.figure(figsize=(8.5,11))

                        plt.subplot(2, 2, (idx%4)+1)

                        _ = plt.hist(plots[node][board][rena][channel]['pha'],bins='auto')
                        plt.title(f"N{node}, B{board}, R{rena}, C{channel}, P{pol}")

                        # Last plot of a page
                        if (idx % 4) == 3:
                            pdf.savefig(fig)
                            fig = None

                        idx += 1

    if fig is not None:
        pdf.savefig(fig)

    pdf.close()

    print("Done Generating plots")

# Save summary data
with open("summary.csv","w") as f:
    print("Creating Summary File")

    f.write("node,board,rena,channel,pol")

    for thold in sumTholds:
        f.write(f",{thold:#03} Hits, {thold:#03} Mean, {thold:#03} Sigma")

    f.write("\n");

    # Init summary Data
    for node in Nodes:
        for board in Boards:
            for rena in range(2):
                for channel in range(36):

                    if channel in sumChannels:
                        pol = summary[node][board][rena][channel]['pol']

                        f.write(f"{node},{board},{rena},{channel},{pol}")

                        for thold in sumTholds:
                            f.write(f",{summary[node][board][rena][channel]['data'][thold]['hits']}")
                            f.write(f",{summary[node][board][rena][channel]['data'][thold]['mean']:.2f}")
                            f.write(f",{summary[node][board][rena][channel]['data'][thold]['sigma']:.2f}")

                        f.write("\n");

    print("Done")

print("Generating summary plot")
outFile = "summary.pdf"

pdf = matplotlib.backends.backend_pdf.PdfPages(outFile)
figs = plt.figure()
fig = None
idx = 0

for node in Nodes:
    for board in Boards:
        for rena in range(2):
            x = []
            y = []
            z = []
            hHits  = []
            hMean  = []
            hSigma = []

            for channel in sumChannels:
                for thold in sumTholds:
                    x.append(channel)
                    y.append(thold)
                    z.append(0)

                    hHits.append(summary[node][board][rena][channel]['data'][thold]['hits'])
                    hMean.append(summary[node][board][rena][channel]['data'][thold]['mean'])
                    hSigma.append(summary[node][board][rena][channel]['data'][thold]['sigma'])

            w = 1
            d = 1

            # 3d summary plot
            fig = plt.figure(figsize=(8.5,11))

            hitFig = fig.add_subplot(3,1,1,projection='3d')
            hitFig.bar3d(x,y,z,w,d,hHits,shade=True)
            hitFig.set_title(f"Hits: N{node}, B{board}, R{rena}, C{channel}, P{pol}")

            meanFig = fig.add_subplot(3,1,2,projection='3d')
            meanFig.bar3d(x,y,z,w,d,hMean,shade=True)
            meanFig.set_title(f"Mean: N{node}, B{board}, R{rena}, C{channel}, P{pol}")

            sigmaFig = fig.add_subplot(3,1,3,projection='3d')
            sigmaFig.bar3d(x,y,z,w,d,hSigma,shade=True)
            sigmaFig.set_title(f"Sigma: N{node}, B{board}, R{rena}, C{channel}, P{pol}")

            pdf.savefig(fig)
            fig = None

            # 3d summary plots
            for channel in sumChannels:
                pol = summary[node][board][rena][channel]['pol']

                hits = []
                mean = []
                sigma = []

                for thold in sumTholds:
                    if thold in summary[node][board][rena][channel]['data']:
                        hits.append(summary[node][board][rena][channel]['data'][thold]['hits'])
                        mean.append(summary[node][board][rena][channel]['data'][thold]['mean'])
                        sigma.append(summary[node][board][rena][channel]['data'][thold]['sigma'])

                    else:
                        hits.append(0)
                        mean.append(0)
                        sigma.append(0)

                fig = plt.figure(figsize=(8.5,11))

                plt.subplot(3, 1, 1)
                _ = plt.bar(sumTholds,hits)
                plt.title(f"Hits: N{node}, B{board}, R{rena}, C{channel}, P{pol}")

                plt.subplot(3, 1, 2)
                _ = plt.bar(sumTholds,mean)
                plt.title(f"Mean: N{node}, B{board}, R{rena}, C{channel}, P{pol}")

                plt.subplot(3, 1, 3)
                _ = plt.bar(sumTholds,sigma)
                plt.title(f"Sigma: N{node}, B{board}, R{rena}, C{channel}, P{pol}")

                pdf.savefig(fig)
                fig = None

pdf.close()

print("Done Generating plots")
