from amelia import *
import json
import pprint

wf = Workflow()

lobSTR = wf.Command("lobSTR",
                    "--p1", inputs.p1 ^ File,
                    "--p2", inputs.p2 ^ File,
                    "--out", inputs.output_prefix ^ str,
                    "--reference", inputs.reference ^ File,
                    "--rg-sample", inputs.rg_sample ^ str,
                    "--rg-lib", inputs.rg_lib ^ str)
lobSTR.bam << Glob(inputs.output_prefix + '.aligned.bam')
lobSTR.bam_stats << Glob(inputs.output_prefix + '.aligned.stats')

samsort = wf.Command("samtools", "sort", lobSTR.bam, "aligned.sorted.bam")
samsort.output_file << Glob("aligned.sorted.bam")

samindex = wf.Run("samtools-index.cwl",
                  input=samsort.output_file)

print(json.dumps(wf.make_wf(), indent=4))
#pprint.pprint(wf.make_wf())
