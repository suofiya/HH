import random

from utils.PathUtil import Path
import time
import fastText
from sklearn.model_selection import train_test_split
from core.preprocess.FastTextPreprocess import FastTextPreprocess
import utils.TimeUtil as tu


class Prediction:
    def __init__(self, name, true_type, predict_type, probs):
        self._name = " ".join(name)
        self._true_type = true_type
        self._predict = predict_type
        self._probes = ""
        for i in range(0, len(probs)):
            self._probes += probs[i][0]+":" + str(probs[i][1]) + " "

    def to_csv_line(self):
        return ",".join([self._name, self._true_type, self._predict, self._probes])+"\n"

    @property
    def true_type(self):
        return self._true_type


def create_label_dict(labels):
    dict = {}
    for i in range(0, len(labels)):
        dict[labels[i]] = i
    return dict


def predict(cls, x_test, y_test, out_file):
    labels = cls.get_labels()
    l_dict = create_label_dict(labels)
    probs = cls.predict_prob(x_test)
    rightNum = 0

    of = open(out_file, "w", encoding="utf-8")
    of.write(','.join(["商品名", "真实类别", "预测类别", "预测概率分布(最大四名)"])+'\n')

    preds =[]
    for i in range(0, len(probs)):
        max = probs[i][0]
        maxIndex = 0
        for j in range(1, len(labels)):
            if probs[i][j] > max:
                max = probs[i][j]
                maxIndex = j
        if maxIndex != l_dict[y_test[i]]:
            dict = {}
            for k in range(0, len(labels)):
                dict[labels[k]] = round(probs[i][k], 2)
            prb_disp = sorted(dict.items(), key=lambda d: d[1], reverse=True)[:4]
            preds.append(Prediction(x_test[i], y_test[i], labels[maxIndex], prb_disp))
        else:
            rightNum += 1
    preds = sorted(preds, key=lambda pred: l_dict[pred.true_type], reverse=True)
    for pred in preds:
        of.write(pred.to_csv_line())
    of.close()
    print("正确数：", rightNum, "总数：", len(probs))


if __name__ == '__main__':
    p = Path()
    f = p.join(p.data_directory, 'tempTrain.txt')
    train_save = p.join(p.save_directory, 'train_801.txt')
    test_save = p.join(p.save_directory, 'test_201.txt')
    model = p.join(p.model_directory, 'temp_model.fs')
    wrongExamples = p.join(p.analyse_directory, 'wrongExamples'+tu.get_formate_time()+'.csv')

    trainP = FastTextPreprocess(p.join(p.data_directory, 'train80(礼品).tsv'), encoding="utf-8")
    testP = FastTextPreprocess(p.test20_1, encoding="utf-8")

    trainP.compile(level=1)
    testP.compile(level=1)
    trainP.save(train_save)
    testP.save(test_save)

    x_train, y_train = trainP.load(train_save)
    x_test, y_test = testP.load(test_save)

    # trainP.update_type(level=1)
    # testP.update_type(level=1)
    #
    # trainP.save(train_save)
    # testP.save(test_save)

    cc = list(zip(x_train, y_train))
    random.shuffle(cc)
    x_train[:], y_train[:] = zip(*cc)

    cls = fastText.fit(x_train, y_train, wordNgrams=2, epoch=10)
    cls.save_model(model)
    # cls = fastText.load_model(model)
    # print(cls.predict_ndarray(x_test,y_test))
    predict(cls, x_test=x_test, y_test=y_test, out_file=wrongExamples)

