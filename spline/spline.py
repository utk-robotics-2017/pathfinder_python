class Spline"
    def calculate(self, out, time):
        raise NotImplementedError("Spline calculate")

    def deriv(self, time):
        raise NotImplementedError("Spline deriv")

    def arc_length(self, samples):
        raise NotImplementedError("Spline calculate")
