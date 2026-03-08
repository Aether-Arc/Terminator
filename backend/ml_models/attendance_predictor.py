from sklearn.linear_model import LinearRegression
import numpy as np

class AttendancePredictor:

    def __init__(self):

        self.model=LinearRegression()

        X=np.array([[100],[200],[300]])
        y=np.array([120,260,380])

        self.model.fit(X,y)

    def predict(self,registrations):

        return int(self.model.predict([[registrations]])[0])