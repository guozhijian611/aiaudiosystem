<template>
  <div class="create">
    <div class="createTop">
      您即将创建一个新用户账户。请填写用户的基本信息（如用户名、密码、角色等），确保信息准确无误。创建成功后，该用户将可以登录并使用系统权限范围内的功能。
    </div>
    <div class="login-bg">
      <div class="login-container">
        <el-form :model="param" :rules="rules" ref="login" size="large">
          <el-form-item prop="username">
            <el-input v-model="param.username" placeholder="用户名">
              <template #prepend>
                <el-icon>
                  <User />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              type="password"
              placeholder="密码"
              v-model="param.password"
              @keyup.enter="submitForm(login)"
            >
              <template #prepend>
                <el-icon>
                  <Lock />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-button
            class="login-btn"
            type="primary"
            size="large"
            @click="submitForm(param.username, param.password)"
            >创建</el-button
          >
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useTabsStore } from "@/store/tabs";
import { usePermissStore } from "@/store/permiss";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import service from "@/utils/request";
import { createuserFn } from "@/api/user";
interface LoginInfo {
  username: string;
  password: string;
}
const lgStr = localStorage.getItem("login-param");
const defParam = lgStr ? JSON.parse(lgStr) : null;
const checked = ref(lgStr ? true : false);

const router = useRouter();
const param = reactive<LoginInfo>({
  username: defParam ? defParam.username : "",
  password: defParam ? defParam.password : "",
});

const rules: FormRules = {
  username: [
    {
      required: true,
      message: "请输入用户名",
      trigger: "blur",
    },
  ],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};
const permiss = usePermissStore();
const login = ref<FormInstance>();
const submitForm = async (username, password) => {
  console.log({username}, {password});
  
  if (!username || !password) {
    ElMessage.error("请填完整信息！");
    return
  } else {
    const res = await createuserFn(username, password);
    console.log(999,res);
    
    if (res.data.code === 200) {
      ElMessage.success("创建成功");
      param.username = "";
      param.password = "";
    } else {
      ElMessage.error(res.data.msg);
    }
  }
};
</script>

<style scoped>
.create {
  background-color: #fff;
  height: 100%;
  box-sizing: border-box;
  overflow: hidden;
}
.createTop {
  padding: 30px 0;
  box-sizing: border-box;
  background-color: #fff;
  border-radius: 5px;
  font-size: 16px;
  color: #333;
  width: 50%;
  margin: 20px auto;
}

.login-bg {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.logo {
  width: 35px;
}

.login-title {
  font-size: 22px;
  color: #333;
  font-weight: bold;
}

.login-container {
  width: 50%;
  margin: 0 auto;
  border-radius: 5px;
  background: #ecedf0;
  padding: 40px 50px 50px;
  box-sizing: border-box;
}

.pwd-tips {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  margin: -10px 0 10px;
  color: #787878;
}

.pwd-checkbox {
  height: auto;
}

.login-btn {
  display: block;
  width: 100%;
}

.login-tips {
  font-size: 12px;
  color: #999;
}

.login-text {
  display: flex;
  align-items: center;
  margin-top: 20px;
  font-size: 14px;
  color: #787878;
}
</style>
