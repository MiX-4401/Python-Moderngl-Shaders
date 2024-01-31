def func(program, buffer, args):
    print(fr"self.ctx.buffer({program}, [({buffer}, {', '.join(args)})])")

func(program="myP", buffer="quad", args=["2f 2f", "bPos", "bTexCoord"])
